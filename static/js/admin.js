/* admin.js — 관리자 CRUD UI */

function switchAdminTab(tab) {
  document.querySelectorAll('.admin-tab-panel').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const panel = document.getElementById(`admin-tab-${tab}`);
  if (panel) panel.classList.remove('hidden');
  event.target.classList.add('active');
  if (tab === 'contents') loadAdminContents();
  else if (tab === 'users') loadAdminUsers();
  else if (tab === 'confirmations') initConfirmationPanel();
}

async function loadAdminContents() {
  const container = document.getElementById('admin-contents-list');
  if (!container) return;
  try {
    const res = await fetch('/api/admin/contents', { credentials: 'include' });
    const data = await res.json();
    if (!data.contents || data.contents.length === 0) {
      container.innerHTML = '<p class="loading-text">등록된 컨텐츠가 없습니다.</p>';
      return;
    }
    let html = `<table class="admin-table"><thead><tr><th>제목</th><th>대상 사번</th><th>응답방식</th><th>작성자</th><th>작업</th></tr></thead><tbody>`;
    data.contents.forEach(c => {
      const atype = c.answer_type === 'text' ? '텍스트' : 'Yes/No';
      html += `<tr data-content-id="${esc(c.content_id)}">
        <td>${esc(c.title)}</td><td>${esc(c.target_emp_id)}</td><td>${atype}</td><td>${esc(c.created_by)}</td>
        <td class="actions">
          <button class="btn btn-ghost btn-sm" onclick="editContent('${c.content_id}')">수정</button>
          <button class="btn btn-danger btn-sm" onclick="deleteContent('${c.content_id}')">삭제</button>
        </td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (e) { container.innerHTML = '<p class="loading-text">불러오기 실패</p>'; }
}

// ── refreshContentTable alias ──
async function refreshContentTable() {
  await loadAdminContents();
}

async function loadAdminUsers() {
  const container = document.getElementById('admin-users-list');
  if (!container) return;
  try {
    const res = await fetch('/api/admin/users', { credentials: 'include' });
    const users = await res.json();
    let html = `<table class="admin-table"><thead><tr><th>사번</th><th>이름</th><th>이메일</th><th>관리자</th><th>활성</th></tr></thead><tbody>`;
    (users || []).forEach(u => {
      html += `<tr><td>${esc(u.emp_id)}</td><td>${esc(u.name)}</td><td>${esc(u.email)}</td>
        <td>${u.is_admin ? '✅' : ''}</td><td>${u.is_active ? '✅' : '❌'}</td></tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (e) { container.innerHTML = '<p class="loading-text">불러오기 실패</p>'; }
}

/* ── 확인 현황 필터 조회 ── */

async function loadConfirmations() {
  const contentId = document.getElementById('filter-content-id').value;
  const empId     = document.getElementById('filter-emp-id').value;

  const params = new URLSearchParams();
  if (contentId) params.append('content_id', contentId);
  if (empId)     params.append('emp_id', empId);

  const container = document.getElementById('admin-confirmations-list');
  try {
    const res = await fetch(`/api/admin/confirmations?${params}`, { credentials: 'include' });
    const rows = await res.json();

    if (!rows || rows.length === 0) {
      container.innerHTML = '<p class="loading-text">조회 결과가 없습니다.</p>';
      return;
    }

    let html = `<table class="admin-table"><thead><tr><th>컨텐츠 ID</th><th>제목</th><th>사번</th><th>이름</th><th>확인 여부</th><th>확인 일시</th></tr></thead><tbody>`;
    rows.forEach(r => {
      const conf = String(r.is_confirmed).toUpperCase() === 'TRUE';
      html += `<tr>
        <td title="${esc(r.content_id)}">${esc(r.content_id).slice(0,8)}…</td>
        <td>${r.title ? esc(r.title) : '-'}</td>
        <td>${esc(r.emp_id)}</td>
        <td>${r.name ? esc(r.name) : '-'}</td>
        <td>${conf ? '✅ 확인' : '⬜ 미확인'}</td>
        <td>${r.confirmed_at && r.confirmed_at !== 'nan' ? esc(r.confirmed_at) : '-'}</td>
      </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (e) { container.innerHTML = '<p class="loading-text">불러오기 실패</p>'; }
}

async function initConfirmationPanel() {
  // 컨텐츠 목록
  const cRes = await fetch('/api/admin/contents', { credentials: 'include' });
  const cData = await cRes.json();
  const contents = cData.contents || [];
  const cSel = document.getElementById('filter-content-id');
  cSel.innerHTML = '<option value="">전체 컨텐츠</option>';
  contents.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.content_id;
    opt.textContent = `${c.title} (${c.content_id.slice(0, 8)}…)`;
    cSel.appendChild(opt);
  });

  // 사용자 목록
  const uRes = await fetch('/api/admin/users', { credentials: 'include' });
  const users = await uRes.json();
  const uSel = document.getElementById('filter-emp-id');
  uSel.innerHTML = '<option value="">전체 대상자</option>';
  (users || []).forEach(u => {
    const opt = document.createElement('option');
    opt.value = u.emp_id;
    opt.textContent = `${u.name} (${u.emp_id})`;
    uSel.appendChild(opt);
  });

  await loadConfirmations();
}

/* ── 새 컨텐츠 모달 열기/닫기 ── */
async function openCreateModal() {
  await loadUserSelectList();
  updateAnswerTypeUI();
  updateSelectedCount();
  document.getElementById("create-content-modal").classList.remove("hidden");
}

function closeCreateModal() {
  document.getElementById("create-content-modal").classList.add("hidden");
  // 입력 초기화
  document.getElementById("content-title").value = "";
  document.getElementById("content-body1").value = "";
  document.getElementById("user-search").value = "";
  document.querySelector('input[name="answer_type"][value="yes_no"]').checked = true;
  updateAnswerTypeUI();
}

// ── 사용자 목록 로드 & 테이블 렌더 ──
let _allUsers = [];

async function loadUserSelectList() {
  const res = await fetch("/api/admin/users", { credentials: "include" });
  _allUsers = await res.json();
  renderUserTable(_allUsers);
}

function renderUserTable(users) {
  const tbody = document.getElementById("user-select-tbody");
  tbody.innerHTML = users.map(u => `
    <tr data-emp-id="${u.emp_id}" data-name="${u.name}">
      <td style="text-align:center;">
        <input type="checkbox" class="user-checkbox" value="${u.emp_id}"
               onchange="updateSelectedCount()">
      </td>
      <td>${u.name}</td>
      <td>${u.emp_id}</td>
      <td style="font-size:12px; color:var(--text-muted);">${u.email ?? ""}</td>
    </tr>
  `).join("");
}

// ── 전체선택 토글 ──
function toggleSelectAll(master) {
  document.querySelectorAll(".user-checkbox").forEach(cb => {
    cb.checked = master.checked;
  });
  updateSelectedCount();
}

// ── 실시간 검색 필터 ──
function filterUserList(query) {
  const q = query.toLowerCase();
  document.querySelectorAll("#user-select-tbody tr").forEach(tr => {
    const name = tr.dataset.name?.toLowerCase() ?? "";
    const id   = tr.dataset.empId?.toLowerCase() ?? "";
    tr.style.display = (name.includes(q) || id.includes(q)) ? "" : "none";
  });
}

// ── 선택 카운트 업데이트 ──
function updateSelectedCount() {
  const count = document.querySelectorAll(".user-checkbox:checked").length;
  document.getElementById("selected-count").textContent = `선택됨: ${count}명`;

  const total = document.querySelectorAll(".user-checkbox").length;
  document.getElementById("select-all-users").checked = count === total && total > 0;
  document.getElementById("select-all-users").indeterminate = count > 0 && count < total;
}

// ── 답변 유형 UI 강조 ──
function updateAnswerTypeUI() {
  const val = document.querySelector('input[name="answer_type"]:checked')?.value;
  document.getElementById("label-yes-no").style.borderColor = val === "yes_no" ? "var(--accent)" : "var(--glass-border)";
  document.getElementById("label-text").style.borderColor   = val === "text"   ? "var(--accent)" : "var(--glass-border)";
}

// ── 컨텐츠 생성 제출 ──
async function submitCreateContent() {
  const title  = document.getElementById("content-title").value.trim();
  const body1  = document.getElementById("content-body1").value.trim();
  const answer = document.querySelector('input[name="answer_type"]:checked')?.value;
  const targets = [...document.querySelectorAll(".user-checkbox:checked")].map(cb => cb.value);

  if (!title)             { alert("제목을 입력하세요."); return; }
  if (!body1)             { alert("내용을 입력하세요."); return; }
  if (targets.length === 0) { alert("대상자를 1명 이상 선택하세요."); return; }

  // 대상자가 여러 명이면 각각 개별 컨텐츠 생성
  const results = await Promise.all(targets.map(emp_id =>
    fetch("/api/admin/contents", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title, body_1: body1,
        target_emp_id: emp_id,
        answer_type: answer,   // "yes_no" | "text"
      }),
    })
  ));

  const failed = results.filter(r => !r.ok).length;
  if (failed > 0) {
    alert(`${targets.length}명 중 ${failed}명 생성 실패. 나머지는 정상 처리되었습니다.`);
  } else {
    alert(`${targets.length}명에게 컨텐츠가 생성되었습니다.`);
  }

  closeCreateModal();
  await refreshContentTable();   // 컨텐츠 목록 갱신
}

/* ── 수정 모달 (기존 유지) ── */

async function loadUserOptions() {
  const res = await fetch('/api/admin/users', { credentials: 'include' });
  const users = await res.json();

  const select = document.getElementById('target-emp-select');
  select.innerHTML = '<option value="">-- 대상자 선택 --</option>';

  (users || []).forEach(({ emp_id, name }) => {
    if (!emp_id) return;
    const opt = document.createElement('option');
    opt.value = emp_id;
    opt.textContent = `${name} (${emp_id})`;
    select.appendChild(opt);
  });
}

async function editContent(contentId) {
  try {
    await loadUserOptions();
    const res = await fetch('/api/admin/contents', { credentials: 'include' });
    const data = await res.json();
    const item = (data.contents || []).find(c => c.content_id === contentId);
    if (!item) return;
    document.getElementById('modal-title').textContent = '컨텐츠 수정';
    document.getElementById('modal-content-id').value = contentId;
    document.getElementById('target-emp-select').value = item.target_emp_id;
    document.getElementById('target-emp-select').disabled = true;
    document.getElementById('modal-title-input').value = item.title;
    document.getElementById('modal-body1').value = item.body_1 || '';
    document.getElementById('modal-body2').value = item.body_2 || '';
    document.getElementById('modal-body3').value = item.body_3 || '';
    document.getElementById('content-modal').classList.remove('hidden');
  } catch (e) { alert('불러오기 실패'); }
}

function closeContentModal() {
  document.getElementById('content-modal').classList.add('hidden');
}

async function submitContentForm() {
  const contentId = document.getElementById('modal-content-id').value;
  const isEdit = !!contentId;

  if (isEdit) {
    const body = {
      title: document.getElementById('modal-title-input').value,
      body_1: document.getElementById('modal-body1').value,
      body_2: document.getElementById('modal-body2').value || null,
      body_3: document.getElementById('modal-body3').value || null,
    };
    try {
      const res = await fetch(`/api/admin/contents/${contentId}`, {
        method: 'PUT', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) { const d = await res.json(); alert(d.detail || '수정 실패'); return; }
    } catch (e) { alert('서버 오류'); return; }
  }
  closeContentModal();
  loadAdminContents();
}

/* ── 삭제 핸들러 ── */

async function deleteContent(contentId) {
  if (!confirm('삭제하면 복구할 수 없습니다. 계속하시겠습니까?')) return;

  const res = await fetch(`/api/admin/contents/${contentId}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (res.ok) {
    // 목록에서 해당 행 즉시 제거
    document.querySelector(`[data-content-id="${contentId}"]`)?.closest('tr')?.remove();
  } else {
    const err = await res.json();
    alert(`삭제 실패: ${err.detail}`);
  }
}

function esc(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }

// 관리자 패널 마운트 시 컨텐츠 목록 자동 로드
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => { if (document.getElementById('admin-contents-list')) loadAdminContents(); }, 500);
});
