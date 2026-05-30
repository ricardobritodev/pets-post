'use strict';

(function () {

  function applyMask(input) {
    const digits = input.value.replace(/\D/g, '').slice(0, 8);
    input.value = digits.length > 5
      ? digits.slice(0, 5) + '-' + digits.slice(5)
      : digits;
  }

  /**
   * Inicializa o lookup de CEP para um par de inputs.
   *
   * @param {string} cepSelector    CSS selector do input de CEP
   * @param {string} targetSelector CSS selector do campo de endereço a preencher
   */
  function initCepLookup(cepSelector, targetSelector) {
    const cepInput = document.querySelector(cepSelector);
    const target   = document.querySelector(targetSelector);

    if (!cepInput || !target) return;

    const statusEl = cepInput.closest('.form-group')
      ? cepInput.closest('.form-group').querySelector('.cep-status')
      : null;

    let controller   = null;
    let debounceTimer = null;

    cepInput.addEventListener('input', function () {
      applyMask(this);
      const digits = this.value.replace(/\D/g, '');
      clearTimeout(debounceTimer);

      if (digits.length !== 8) {
        setStatus('');
        return;
      }

      debounceTimer = setTimeout(function () { fetchCep(digits); }, 500);
    });

    async function fetchCep(cep) {
      if (controller) controller.abort();
      controller = new AbortController();
      setStatus('loading');

      try {
        const res  = await fetch('/api/cep/' + cep, { signal: controller.signal });
        const data = await res.json();

        if (!res.ok || data.erro) {
          setStatus('error', data.erro || 'CEP não encontrado');
          return;
        }

        const parts = [data.logradouro, data.bairro].filter(Boolean);
        const city  = (data.localidade && data.uf)
          ? data.localidade + '/' + data.uf
          : (data.localidade || '');

        // Usa textContent via value — nunca innerHTML
        target.value = [...parts, city].filter(Boolean).join(', ');
        setStatus('ok');
        target.focus();
      } catch (e) {
        if (e.name !== 'AbortError') {
          setStatus('error', 'Erro ao consultar CEP');
        }
      }
    }

    function setStatus(state, msg) {
      if (!statusEl) return;
      statusEl.textContent = '';
      statusEl.className = 'cep-status';
      if (state === 'loading') {
        statusEl.textContent = 'Buscando endereço...';
        statusEl.classList.add('cep-status--loading');
      } else if (state === 'ok') {
        statusEl.textContent = '✓ Endereço preenchido';
        statusEl.classList.add('cep-status--ok');
      } else if (state === 'error') {
        statusEl.textContent = msg || 'CEP não encontrado';
        statusEl.classList.add('cep-status--error');
      }
    }
  }

  window.initCepLookup = initCepLookup;

  document.addEventListener('DOMContentLoaded', function () {
    initCepLookup('#cep-input', '#location-field');
  });

}());
