from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
import mimetypes, io
from urllib.parse import quote, unquote
from django.db.models import F



from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication


from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from file_versions.models import FileVersion
from .serializers import FileVersionSerializer
from django.contrib.auth import get_user_model

class FileVersionViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = []
    serializer_class = FileVersionSerializer
    # queryset = FileVersion.objects.none()
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        return super().list(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        print(self.request.user)
        return FileVersion.objects.filter(owned_by=self.request.user.id)

    def create(self, request):
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        # Get the file object from the request
        file_obj = request.data['file']
        url = request.POST.get('url')
        version = 0

        try:
            version = int(request.POST.get('version'))
        except BaseException as e:
            print(e)

        # Read the file data
        if isinstance(file_obj, InMemoryUploadedFile):
            file_data = file_obj.read()

            old_record = FileVersion.objects.filter(owned_by= request.user.id, file_name= file_obj.name, file_url=
                                                    quote(f'''{url}{'/' if url else ''}{file_obj.name}'''), version_number=version).order_by('-version_number')
            record = FileVersion.objects.filter(owned_by= request.user.id, file_name= file_obj.name, file_url=
                                                quote(f'''{url}{'/' if url else ''}{file_obj.name}''')).order_by('-version_number')
            
            if old_record.exists():
                # old_record[0].file_binary = file_data
                # old_record.save()
                old_record.update(file_binary=file_data, created_on=timezone.now())
                return Response(status=HTTP_200_OK)
            elif record.exists():
               version = record[0].version_number + 1

            # Validate and save the file using the serializer
            serializer = FileVersionSerializer(data={
                'file_name'     : file_obj.name,
                'owned_by'      : request.user.id,
                'file_binary'   : file_data,
                'file_url'      : quote(f'''{url}{'/' if url else ''}{file_obj.name}'''),
                'created_on'    : timezone.now(),
                'version_number': version
                }
                )
            if serializer.is_valid():
                serializer.save()
                serializer.instance.file_binary = file_data
                print(type(file_data))
                serializer.instance.save()
                return Response(serializer.data, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse(status=400)

    # def update(self, request):
    #     # Get the file object from the request
    #     file_obj = request.data['file']
    #     url = request.PUT.get('url')
    #     version = request.PUT.get('version')
    #     # Read the file data
    #     if isinstance(file_obj, InMemoryUploadedFile):
    #         file_data = file_obj.read()
            
    #         old_record = FileVersion.objects.filter(owned_by= request.user.id, file_name= file_obj.name, file_url=quote(f'''{url}{'/' if url else ''}{file_obj.name}'''), version_number=version).order_by('-version_number').first()
    #         if old_record:
    #             old_record.file_binary = file_data
    #             old_record.save()
    #             return Response(old_record.data, status=HTTP_200_OK)
    #         else:
    #             return Response(old_record.errors, status=HTTP_400_BAD_REQUEST)
    #     else:
    #         return HttpResponse(status=400)

def download_file(request, fpath):
    vno = request.GET.get('revision')
    url = fpath
    file = None
    obj = FileVersion.objects.filter(file_url=quote(f'{url}'), owned_by=request.user.id)
    if vno:
        obj = obj.filter(version_number=int(vno)).order_by('-created_on').first()
    else:
        obj = obj.order_by('-version_number', "-created_on").first()
    if obj:
        mime_type, encoding = mimetypes.guess_type(obj.file_url.split('/')[-1])
        response = FileResponse(io.BytesIO(obj.file_binary), as_attachment=True, filename=unquote(obj.file_url).split('/')[-1], content_type=mime_type)
        return response
    else:
        return HttpResponse(status=404)


def upload_file_page(request):

    return render(request, 'upload.html', {})

# def upload_revision_page(request):
#     return render(request, 'upload_revision.html', {})




