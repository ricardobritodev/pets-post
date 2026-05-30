/**
 * main.js — Scripts Globais do Pets Post
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
  // 3. Máscara de telefone
  // -----------------------------------------------
  initPhoneMask();

  // -----------------------------------------------
  // 4. Validação de email em tempo real
  // -----------------------------------------------
  initEmailValidation();

  // -----------------------------------------------
  // 5. Upload de fotos (drag-and-drop)
  // -----------------------------------------------
  initPhotoUpload();

  // -----------------------------------------------
  // 6. data-confirm — confirmação antes de ações destrutivas
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
  // 7. data-form-submit — botões que disparam forms externos
  // -----------------------------------------------
  document.querySelectorAll('[data-form-submit]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var formId = this.getAttribute('data-form-submit');
      var form = document.getElementById(formId);
      if (form) form.submit();
    });
  });

  // -----------------------------------------------
  // 8. Filtros dinâmicos sem reload (F-10)
  // -----------------------------------------------
  initDynamicFilters();

  // -----------------------------------------------
  // 9. Menu hambúrguer para mobile (F-11)
  // -----------------------------------------------
  initHamburgerMenu();

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

// ================================================================
// MENU HAMBÚRGUER (F-11)
// Toggle da classe is-open na navbar, com atualização de
// aria-expanded e fechamento em 4 situações:
//   1. Clique no botão toggle
//   2. Clique em qualquer link do menu
//   3. Clique fora da navbar
//   4. Tecla Escape
//   5. Redimensionamento para desktop (≥ 769px)
// ================================================================

function initHamburgerMenu() {
  var navbar     = document.querySelector('.navbar');
  var toggle     = document.querySelector('.navbar__toggle');
  var mobileMenu = document.getElementById('mobile-menu');

  if (!toggle) return;

  // 1. Abre/fecha ao clicar no botão
  toggle.addEventListener('click', function (e) {
    e.stopPropagation();
    var willOpen = !navbar.classList.contains('is-open');
    setMenuState(willOpen);
  });

  // 2. Fecha ao clicar em qualquer link ou botão do menu mobile
  if (mobileMenu) {
    mobileMenu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON') {
        setMenuState(false);
      }
    });
  }

  // 3. Fecha ao clicar fora da navbar
  document.addEventListener('click', function (e) {
    if (!navbar.contains(e.target)) {
      setMenuState(false);
    }
  });

  // 4. Fecha com a tecla Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && navbar.classList.contains('is-open')) {
      setMenuState(false);
      toggle.focus(); // devolve foco ao botão para não perder contexto
    }
  });

  // 5. Fecha ao redimensionar para desktop
  window.addEventListener('resize', function () {
    if (window.innerWidth > 768) {
      setMenuState(false);
    }
  });

  function setMenuState(open) {
    navbar.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute(
      'aria-label',
      open ? 'Fechar menu de navegação' : 'Abrir menu de navegação'
    );
  }
}

// ================================================================
// MÁSCARA DE TELEFONE BRASILEIRO
// Aceita fixo (XX) XXXX-XXXX e celular (XX) XXXXX-XXXX.
// Aplica-se a todos os input[type=tel].
// ================================================================

function initPhoneMask() {
  document.querySelectorAll('input[type=tel]').forEach(function (input) {
    input.setAttribute('maxlength', '15');
    input.addEventListener('input', function () {
      var digits = this.value.replace(/\D/g, '').slice(0, 11);
      var masked = '';
      if (digits.length === 0) {
        masked = '';
      } else if (digits.length <= 2) {
        masked = '(' + digits;
      } else if (digits.length <= 6) {
        masked = '(' + digits.slice(0, 2) + ') ' + digits.slice(2);
      } else if (digits.length <= 10) {
        // Fixo: (XX) XXXX-XXXX
        masked = '(' + digits.slice(0, 2) + ') ' + digits.slice(2, 6) + '-' + digits.slice(6);
      } else {
        // Celular: (XX) XXXXX-XXXX
        masked = '(' + digits.slice(0, 2) + ') ' + digits.slice(2, 7) + '-' + digits.slice(7);
      }
      this.value = masked;
    });
  });
}

// ================================================================
// VALIDAÇÃO DE EMAIL EM TEMPO REAL
// Verifica formato mínimo (algo@algo.algo) no evento blur.
// ================================================================

function initEmailValidation() {
  document.querySelectorAll('input[type=email]').forEach(function (input) {
    input.addEventListener('blur', function () {
      var val = this.value.trim();

      // Remove erro anterior gerado por este script
      var prev = this.parentNode.querySelector('.field-error--email-js');
      if (prev) prev.remove();

      // Campo vazio e não obrigatório: sem mensagem
      if (!val && !this.required) return;

      // Validação: precisa de @, algo antes e algo.algo depois
      var valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
      if (!valid) {
        var err = document.createElement('span');
        err.className = 'field-error field-error--email-js';
        err.textContent = 'Informe um email válido (ex: nome@dominio.com).';
        this.parentNode.appendChild(err);
      }
    });

    // Remove o erro ao começar a digitar novamente
    input.addEventListener('input', function () {
      var prev = this.parentNode.querySelector('.field-error--email-js');
      if (prev) prev.remove();
    });
  });
}

// ================================================================
// UPLOAD DE FOTOS COM DRAG-AND-DROP
// Create pages: drop zone + preview em grid + contador.
// Edit pages (form[data-edit-mode]): botão × nas fotos existentes.
// ================================================================

var MAX_PHOTOS = 6;

function initPhotoUpload() {
  var zone      = document.getElementById('upload-zone');
  var input     = document.getElementById('photos');
  var preview   = document.getElementById('photo-preview');
  var counter   = document.getElementById('upload-counter');
  var form      = document.querySelector('form[data-edit-mode]');
  var deleteFld = document.getElementById('photos-to-delete');

  // ── Drag-and-drop / click para criar post ───────────────────────
  if (zone && input && preview) {
    // Abre o file picker ao clicar na zona
    zone.addEventListener('click', function () { input.click(); });

    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('is-dragging');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('is-dragging');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('is-dragging');
      applyFiles(e.dataTransfer.files);
    });

    input.addEventListener('change', function () {
      applyFiles(this.files);
    });

    function applyFiles(fileList) {
      var files = Array.from(fileList).filter(function (f) { return f.type.startsWith('image/'); });

      // Remove erro anterior
      var prev = zone.parentNode.querySelector('.field-error--js');
      if (prev) prev.remove();

      if (files.length > MAX_PHOTOS) {
        showZoneError(zone, 'Selecione no máximo ' + MAX_PHOTOS + ' fotos.');
        input.value = '';
        return;
      }

      // Recria a lista de arquivos no input via DataTransfer
      var dt = new DataTransfer();
      files.forEach(function (f) { dt.items.add(f); });
      input.files = dt.files;

      renderPreviews(files, preview, counter, input);
    }
  }

  // ── Deleção de fotos no edit ────────────────────────────────────
  if (form && deleteFld) {
    var toDelete = [];

    document.querySelectorAll('.photo-grid-item__remove').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = this.dataset.photoId;
        var card = this.closest('.photo-grid-item');
        if (!id || !card) return;

        toDelete.push(id);
        deleteFld.value = toDelete.join(',');
        card.classList.add('marked-for-delete');
        btn.disabled = true;
      });
    });
  }

  // ── Preview drag-and-drop do edit (adicionar novas fotos) ───────
  if (!zone && input && preview) {
    input.addEventListener('change', function () {
      var files = Array.from(this.files).filter(function (f) { return f.type.startsWith('image/'); });
      renderPreviews(files, preview, null, null);
    });
  }
}

function renderPreviews(files, container, counter, input) {
  container.innerHTML = '';
  if (counter) counter.textContent = files.length + ' / ' + MAX_PHOTOS;

  files.forEach(function (file, idx) {
    var reader = new FileReader();
    reader.onload = function (e) {
      var item = document.createElement('div');
      item.className = 'photo-grid-item';

      var img = document.createElement('img');
      img.src = e.target.result;
      img.alt = file.name;

      var removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'photo-grid-item__remove';
      removeBtn.setAttribute('aria-label', 'Remover foto');
      removeBtn.textContent = '×';
      removeBtn.addEventListener('click', function () {
        item.remove();
        // Recria o input sem esse arquivo
        if (input) {
          var dt = new DataTransfer();
          Array.from(input.files).forEach(function (f, i) {
            if (i !== idx) dt.items.add(f);
          });
          input.files = dt.files;
        }
        var counter2 = document.getElementById('upload-counter');
        if (counter2) counter2.textContent = container.querySelectorAll('.photo-grid-item').length + ' / ' + MAX_PHOTOS;
      });

      item.appendChild(img);
      item.appendChild(removeBtn);
      container.appendChild(item);
    };
    reader.readAsDataURL(file);
  });
}

function showZoneError(zone, msg) {
  var err = document.createElement('span');
  err.className = 'field-error field-error--js';
  err.textContent = msg;
  zone.parentNode.insertBefore(err, zone.nextSibling);
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
