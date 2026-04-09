/**
 * main.js — Scripts Globais do PetPost
 *
 * Funcionalidades:
 *   1. Fechar flash messages
 *   2. Preview de fotos no upload
 *   3. Confirmação antes de deletar
 *   4. Filtros de posts na home (sem recarregar a página)
 */

// Executa quando o HTML terminou de carregar
document.addEventListener('DOMContentLoaded', function () {

  // -----------------------------------------------
  // 1. Fechar flash messages ao clicar no X
  // -----------------------------------------------
  document.querySelectorAll('.flash__close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      // Remove a mensagem do DOM ao clicar no botão fechar
      this.closest('.flash').remove();
    });
  });

  // Auto-fechar flash messages após 5 segundos
  setTimeout(function () {
    document.querySelectorAll('.flash').forEach(function (flash) {
      flash.style.transition = 'opacity 0.5s ease';
      flash.style.opacity = '0';
      setTimeout(function () { flash.remove(); }, 500);
    });
  }, 5000);

  // -----------------------------------------------
  // 2. Preview de fotos antes do upload
  // -----------------------------------------------
  var photoInput = document.getElementById('photos');
  var previewContainer = document.getElementById('photo-preview');

  if (photoInput && previewContainer) {
    photoInput.addEventListener('change', function () {
      // Limpa os previews anteriores
      previewContainer.innerHTML = '';

      var files = Array.from(this.files);

      // Máximo de 5 fotos
      if (files.length > 5) {
        alert('Você pode enviar no máximo 5 fotos por post.');
        this.value = '';
        return;
      }

      files.forEach(function (file) {
        if (!file.type.startsWith('image/')) return;

        var reader = new FileReader();
        reader.onload = function (e) {
          var wrapper = document.createElement('div');
          wrapper.style.cssText = 'position:relative; display:inline-block;';

          var img = document.createElement('img');
          img.src = e.target.result;
          img.style.cssText = 'width:100px; height:100px; object-fit:cover; border-radius:8px; border:2px solid #dee2e6;';

          wrapper.appendChild(img);
          previewContainer.appendChild(wrapper);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // -----------------------------------------------
  // 3. Confirmação antes de deletar um post
  // -----------------------------------------------
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      var message = this.getAttribute('data-confirm') || 'Tem certeza?';
      if (!confirm(message)) {
        e.preventDefault();
        return false;
      }
    });
  });

  // -----------------------------------------------
  // 4. Submit de formulários de confirmação (delete, resolve)
  //    Botões com data-form-submit disparam o form pai pelo ID
  // -----------------------------------------------
  document.querySelectorAll('[data-form-submit]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      var formId = this.getAttribute('data-form-submit');
      var form = document.getElementById(formId);
      if (form) form.submit();
    });
  });

});

// TODO: Implementar busca em tempo real nos posts (filtro no frontend)
// TODO: Implementar mapa com Google Maps ou Leaflet.js
// TODO: Implementar validação de formulário no frontend para feedback imediato
// TODO: Implementar menu hambúrguer para mobile
