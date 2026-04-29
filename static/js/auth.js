/* auth.js — OTP 요청/검증 로직 */

let _currentEmpId = '';

function showMessage(text, type = 'error') {
  const el = document.getElementById('auth-message');
  if (!el) return;
  el.textContent = text;
  el.className = `message ${type}`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 5000);
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  const text = btn.querySelector('.btn-text');
  const loader = btn.querySelector('.btn-loader');
  if (loading) {
    btn.disabled = true;
    if (text) text.classList.add('hidden');
    if (loader) loader.classList.remove('hidden');
  } else {
    btn.disabled = false;
    if (text) text.classList.remove('hidden');
    if (loader) loader.classList.add('hidden');
  }
}

async function requestOTP() {
  const empId = document.getElementById('input-emp-id').value.trim();
  if (!empId) { showMessage('사번을 입력해주세요.'); return; }

  setLoading('btn-request-otp', true);
  try {
    const res = await fetch('/auth/step1', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emp_id: empId })
    });
    const data = await res.json();
    if (!res.ok) { showMessage(data.detail || '요청에 실패했습니다.'); return; }

    _currentEmpId = empId.toUpperCase();
    document.getElementById('otp-email-hint').textContent = data.email_hint || '';
    document.getElementById('auth-step1').classList.add('hidden');
    document.getElementById('auth-step2').classList.remove('hidden');
    showMessage('인증 코드가 발송되었습니다.', 'success');
    document.getElementById('input-otp').focus();
  } catch (e) {
    showMessage('서버 연결에 실패했습니다.');
  } finally {
    setLoading('btn-request-otp', false);
  }
}

async function verifyOTP() {
  const otp = document.getElementById('input-otp').value.trim();
  if (!otp || otp.length !== 6) { showMessage('6자리 인증 코드를 입력해주세요.'); return; }

  setLoading('btn-verify-otp', true);
  try {
    const res = await fetch('/auth/step2', {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emp_id: _currentEmpId, otp })
    });
    const data = await res.json();
    if (!res.ok) { showMessage(data.detail || '인증에 실패했습니다.'); return; }

    showMessage('인증 성공! 페이지를 이동합니다.', 'success');
    setTimeout(() => { window.location.href = '/app'; }, 800);
  } catch (e) {
    showMessage('서버 연결에 실패했습니다.');
  } finally {
    setLoading('btn-verify-otp', false);
  }
}

function backToStep1() {
  document.getElementById('auth-step2').classList.add('hidden');
  document.getElementById('auth-step1').classList.remove('hidden');
  document.getElementById('input-otp').value = '';
}

// Enter 키 지원
document.addEventListener('DOMContentLoaded', () => {
  const empInput = document.getElementById('input-emp-id');
  const otpInput = document.getElementById('input-otp');
  if (empInput) empInput.addEventListener('keydown', e => { if (e.key === 'Enter') requestOTP(); });
  if (otpInput) otpInput.addEventListener('keydown', e => { if (e.key === 'Enter') verifyOTP(); });
});
