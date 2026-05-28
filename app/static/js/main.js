/**
 * main.js — Scripts Globais do PetPost
 */

document.addEventListener('DOMContentLoaded', function () {

  // -----------------------------------------------
  // 1. Fechar flash messages ao clicar no X
  // -----------------------------------------------
  document.querySelectorAll('.flash__close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      this.closest('.flash').remove();
    });
  });

  // Auto-fechar flash messages após 6 segundos
  setTimeout(function () {
    document.querySelectorAll('.flash').forEach(function (flash) {
      flash.style.transition = 'opacity 0.5s ease';
      flash.style.opacity = '0';
      setTimeout(function () { flash.remove(); }, 500);
    });
  }, 6000);

  // -----------------------------------------------
  // 2. Galeria de miniaturas — troca a foto principal
  // -----------------------------------------------
  var mainPhoto = document.getElementById('main-photo');
  if (mainPhoto) {
    document.querySelectorAll('.gallery-thumb').forEach(function (thumb) {
      thumb.addEventListener('click', function () {
        mainPhoto.src = this.dataset.src;
        mainPhoto.alt = this.alt;
        document.querySelectorAll('.gallery-thumb').forEach(function (t) {
          t.classList.remove('active');
        });
        this.classList.add('active');
      });
    });
  }

  // -----------------------------------------------
  // 3. Preview de fotos antes do upload
  // -----------------------------------------------
  var photoInput = document.getElementById('photos');
  var previewContainer = document.getElementById('photo-preview');

  if (photoInput && previewContainer) {
    photoInput.addEventListener('change', function () {
      previewContainer.innerHTML = '';

      var existingError = photoInput.parentNode.querySelector('.field-error--js');
      if (existingError) existingError.remove();

      var files = Array.from(this.files);

      if (files.length > 5) {
        var errorEl = document.createElement('span');
        errorEl.className = 'field-error field-error--js';
        errorEl.textContent = 'Selecione no máximo 5 fotos por post.';
        photoInput.parentNode.insertBefore(errorEl, previewContainer);
        this.value = '';
        return;
      }

      files.forEach(function (file) {
        if (!file.type.startsWith('image/')) return;

        var reader = new FileReader();
        reader.onload = function (e) {
          var img = document.createElement('img');
          img.src = e.target.result;
          img.style.cssText = 'width:100px; height:100px; object-fit:cover; border-radius:var(--radius-md,8px); border:2px solid var(--color-border,#dee2e6);';
          img.alt = file.name;
          previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // -----------------------------------------------
  // 4. data-confirm — confirmação antes de ações destrutivas
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
  // 5. data-form-submit — botões que disparam forms externos
  // -----------------------------------------------
  document.querySelectorAll('[data-form-submit]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var formId = this.getAttribute('data-form-submit');
      var form = document.getElementById(formId);
      if (form) form.submit();
    });
  });

  // -----------------------------------------------
  // 6. Filtros dinâmicos sem reload (F-10)
  // -----------------------------------------------
  initDynamicFilters();

});

// ================================================================
// FILTROS DINÂMICOS
// Intercepta cliques nos filtros e na paginação da página /posts,
// busca apenas o partial HTML do grid via AJAX e troca o conteúdo
// sem recarregar a página. Mantém a URL sincronizada com pushState.
// Degradação graciosa: se fetch falhar, navega normalmente.
// ================================================================

function initDynamicFilters() {
  var grid = document.getElementById('posts-grid');
  if (!grid) return; // Só executa na página de listagem

  // Intercepta cliques nos botões de filtro (fora do grid)
  var filtersEl = document.getElementById('filters');
  if (filtersEl) {
    filtersEl.addEventListener('click', function (e) {
      var link = e.target.closest('.filter-btn');
      if (!link) return;
      e.preventDefault();
      fetchGrid(new URL(link.href), true);
    });
  }

  // Event delegation para links de paginação gerados dentro do grid
  grid.addEventListener('click', function (e) {
    var link = e.target.closest('.pagination a');
    if (!link) return;
    e.preventDefault();
    fetchGrid(new URL(link.href), true);
  });

  // Suporte ao botão Voltar/Avançar do navegador
  window.addEventListener('popstate', function () {
    fetchGrid(new URL(window.location.href), false);
  });
}

function fetchGrid(url, pushState) {
  var grid = document.getElementById('posts-grid');
  if (!grid) return;

  // Estado de carregamento: visual feedback sem travar interação
  grid.classList.add('is-loading');

  fetch(url.href, {
    method: 'GET',
    headers: {
      // Header que sinaliza ao Flask para retornar apenas o partial
      'X-Requested-With': 'XMLHttpRequest'
    },
    // Sem credentials extras — requisição para mesma origem
    credentials: 'same-origin'
  })
    .then(function (response) {
      if (!response.ok) {
        // Erro HTTP (500, 404 etc.) — fallback para navegação normal
        throw new Error('HTTP ' + response.status);
      }
      return response.text();
    })
    .then(function (html) {
      grid.innerHTML = html;

      // Sincroniza URL no navegador
      if (pushState) {
        history.pushState(null, '', url.pathname + url.search);
      }

      // Atualiza estado visual dos botões de filtro
      syncFilterButtons(url);

      // Rola suavemente para o topo do grid se estava abaixo dele
      var gridTop = grid.getBoundingClientRect().top + window.scrollY;
      if (window.scrollY > gridTop) {
        window.scrollTo({ top: gridTop - 80, behavior: 'smooth' });
      }
    })
    .catch(function () {
      // Fallback: navegação normal — o filtro ainda funciona
      window.location.href = url.href;
    })
    .finally(function () {
      grid.classList.remove('is-loading');
    });
}

// Marca como ativo o botão cujos query params coincidem com a URL atual
function syncFilterButtons(url) {
  var currentParams = url.searchParams;
  var filtersEl = document.getElementById('filters');
  if (!filtersEl) return;

  filtersEl.querySelectorAll('.filter-btn').forEach(function (btn) {
    var btnParams = new URL(btn.href).searchParams;

    // Botão "Todos" não tem params; ativo quando a URL também não tem filtro
    var isAllBtn = !btnParams.has('status') && !btnParams.has('pet_type');
    var noActiveFilter = !currentParams.has('status') && !currentParams.has('pet_type');

    var isActive = isAllBtn
      ? noActiveFilter
      : Array.from(btnParams.entries()).every(function (entry) {
          return currentParams.get(entry[0]) === entry[1];
        });

    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-current', isActive ? 'true' : 'false');
  });
}
