from django.shortcuts import render, redirect, get_object_or_404
from .models import Paste, Language
from .encryption import encrypt, decrypt  # Import your encryption functions

def create_paste(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        password = request.POST.get('password')
        lang = get_object_or_404(Language, id=request.POST.get('language'))

        if content:  # Check if content is provided
            if password:  # If a password is provided, encrypt the content
                salt, iv, ciphertext = encrypt(content, password)
                Paste.objects.create(salt=salt, iv=iv, ciphertext=ciphertext, lang=lang)
            else:  # If no password, store the content as is
                Paste.objects.create(salt=None, iv=None, ciphertext=content, lang=lang)
            return redirect('home')

    languages = Language.objects.all()
    return render(request, 'create.html', {'languages': languages})

def view_encrypted_paste(request, paste_id):
    paste = get_object_or_404(Paste, id=paste_id)

    if paste.salt:
        if request.method == 'POST':
            password = request.POST.get('password')
            if password:
                try:
                    decrypted_content = decrypt(paste.salt, paste.iv, paste.ciphertext, password)
                    return render(request, 'view.html', {'content': decrypted_content, 'lang': paste.lang})
                except Exception as e:
                    print(f"Decryption error: {e}")
                    return render(request, 'view.html', {'error': 'Incorrect password. Please try again.', 'lang': paste.lang})

        return render(request, 'view.html', {'lang': paste.lang, 'has_password': True})
    else:
        decrypted_content = paste.ciphertext
        return render(request, 'view.html', {'content': decrypted_content, 'lang': paste.lang})

def home(request):
    pastes = Paste.objects.all()
    return render(request, 'home.html', {'pastes': pastes})
