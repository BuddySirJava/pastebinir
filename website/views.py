import hashlib
import random
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from .models import Paste, Language
from .encryption import encrypt, decrypt

def generate_unique_id():
    while True:
        unique_string = f"{timezone.now().timestamp()}{random.randint(0, 999999)}"
        hash_object = hashlib.sha256(unique_string.encode())
        unique_id = hash_object.hexdigest()[:6]
        if not Paste.objects.filter(id=unique_id).exists():
            return unique_id

def pasteCheck(paste):
    if paste.one_time and paste.view_count > 1:
        return False
    if paste.expires and paste.expires < timezone.now():
        return False
    return True




def create_paste(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        password = request.POST.get('password')
        lang = get_object_or_404(Language, id=request.POST.get('language'))
        expiration_days = request.POST.get('expiration')
        one_time = request.POST.get('one_time') == 'on'

        if content:
            id = generate_unique_id()
            expires = None
            if expiration_days:
                expires = timezone.now() + timedelta(days=int(expiration_days))
            if password:
                salt, iv, ciphertext = encrypt(content, password)
                Paste.objects.create(id=id, salt=salt, iv=iv, ciphertext=ciphertext, lang=lang, expires=expires,
                                     one_time=one_time)
            else:
                Paste.objects.create(id=id, salt=None, iv=None, ciphertext=content, lang=lang, expires=expires,
                                     one_time=one_time)

            pastes_cookie = request.COOKIES.get('pasteHistory', '')
            if pastes_cookie:
                pastes_list = pastes_cookie.split(',')
                if id not in pastes_list:
                    pastes_list.append(id)
            else:
                pastes_list = [id]
            print("triggered 3")
            response = redirect('view_encrypted_paste', paste_id=id)
            response.set_cookie('pasteHistory', ','.join(pastes_list), max_age=31536000)
            return response

    languages = Language.objects.all()
    return render(request, 'create.html', {'languages': languages})

def about(request):
    return render(request,'about.html')

def view_encrypted_paste(request, paste_id):
    paste = get_object_or_404(Paste, id=paste_id)

    if not pasteCheck(paste):
        paste.delete()
        return render(request, 'view.html', {'error': 'This paste is no longer available.'})

    if paste.salt:
        if request.method == 'POST':
            password = request.POST.get('password')
            if password:
                try:
                    decrypted_content = decrypt(paste.salt, paste.iv, paste.ciphertext, password)
                    paste.view_count += 1
                    paste.save()
                    return render(request, 'view.html', {'content': decrypted_content, 'lang': paste.lang})
                except Exception as e:
                    print(f"Decryption error: {e}")
                    return render(request, 'view.html', {'error': 'Incorrect password. Please try again.', 'lang': paste.lang})
        paste.view_count += 1
        paste.save()
        print("Triggered 1")
        return render(request, 'view.html', {'lang': paste.lang, 'has_password': True})

    else:
        decrypted_content = paste.ciphertext
        paste.view_count += 1
        paste.save()
        print("Triggered 2")
        return render(request, 'view.html', {'content': decrypted_content, 'lang': paste.lang})

def history(request):
    pastes = []
    pastes_cookie = request.COOKIES.get('pasteHistory', '')
    if pastes_cookie:
        paste_ids = pastes_cookie.split(',')
        pastes = Paste.objects.filter(id__in=paste_ids)
    return render(request, 'history.html', {'pastes': pastes})
def err404(request, exception):
    return render(request,'404.html',status=404)

