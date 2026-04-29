/* content.js — 레이어 동적 주입 및 컨텐츠 확인 */

async function mountLayer(layerId, fragmentUrl) {
  try {
    const res = await fetch(fragmentUrl, { credentials: 'include' });
    if (!res.ok) return;
    const html = await res.text();
    const target = document.getElementById(layerId);
    if (!target) return;
    target.innerHTML = html;
    target.classList.remove('hidden');
  } catch (e) {
    console.error(`Layer mount failed: ${layerId}`, e);
  }
}

// Yes / No 응답
async function handleYesNo(contentId, answer) {
  const res = await fetch(`/api/content/${contentId}/confirm`, {
    method: "PATCH",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed: true, answer_type: "yes_no", text: answer }),
  });
  if (res.ok) {
    // 버튼 영역을 완료 뱃지로 교체
    const card = document.querySelector(`[data-content-id="${contentId}"]`);
    const btnWrap = card?.querySelector(".yesno-wrap");
    if (btnWrap) {
      btnWrap.outerHTML = `<span style="display:inline-block;padding:8px 20px;margin-top:1rem;
        border-radius:6px;background:var(--success-bg);color:var(--success);font-weight:600;">
        ✅ ${answer}</span>`;
    }
    // 카드 확인 상태 표시
    if (card) card.classList.add('confirmed');
  } else {
    alert("저장에 실패했습니다.");
  }
}

// 문구 입력 응답
async function handleTextSubmit(contentId) {
  const textarea = document.getElementById(`text-${contentId}`);
  const text = textarea.value.trim();
  if (!text) { alert('내용을 입력해주세요.'); return; }

  const res = await fetch(`/api/content/${contentId}/confirm`, {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirmed: true, answer_type: 'text', text }),
  });

  if (res.ok) {
    textarea.readOnly = true;
    // 제출 버튼 제거 후 완료 뱃지
    const btn = textarea.parentElement.querySelector('button');
    if (btn) btn.remove();
    const badge = document.createElement('span');
    badge.style.cssText = 'display:inline-block;margin-top:0.5rem;color:var(--success);font-weight:600;';
    badge.textContent = '✅ 제출 완료';
    textarea.insertAdjacentElement('afterend', badge);
    // 카드 확인 상태 표시
    const card = textarea.closest('.content-card');
    if (card) card.classList.add('confirmed');
  } else {
    alert('제출에 실패했습니다.');
  }
}

async function handleLogout() {
  try {
    await fetch('/auth/logout', { method: 'POST', credentials: 'include' });
  } catch (e) { /* ignore */ }
  window.location.href = '/app';
}

document.addEventListener('DOMContentLoaded', async () => {
  const state = window.__APP_STATE__;
  if (!state) return;

  if (!state.isAuthenticated) {
    await mountLayer('layer-auth', '/fragment/auth');
    return;
  }
  await mountLayer('layer-content', '/fragment/content');
  if (state.isAdmin) {
    await mountLayer('layer-admin', '/fragment/admin');
  }
});
