/* ==========================================================================
   LINUXQUEST — MAIN INTERACTION & API CONTROLLER
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  console.log("LinuxQuest Platform initialized.");
});

function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: rgba(10, 16, 26, 0.95);
    border: 1px solid ${type === 'success' ? '#00ff9d' : '#00f3ff'};
    color: #fff;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    z-index: 9999;
    font-weight: 600;
    transition: all 0.3s ease;
  `;
  toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle text-green' : 'info-circle text-cyan'}"></i> ${message}`;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

async function markLessonCompleted(lessonId) {
  try {
    const res = await fetch(`/api/lessons/${lessonId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.success) {
      if (window.soundEngine) window.soundEngine.playSuccessSound();
      showToast(`Lesson Completed! +${data.xp_earned || 50} XP Earned!`, 'success');
      const btn = document.getElementById('completeLessonBtn');
      if (btn) {
        btn.innerHTML = `<i class="fas fa-check-circle"></i> Completed!`;
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-success');
        btn.disabled = true;
      }
    }
  } catch (err) {
    showToast("Error completing lesson", "error");
  }
}

async function submitQuizForm(quizId) {
  const form = document.getElementById('quizForm');
  if (!form) return;

  const formData = new FormData(form);
  const answers = {};
  for (const [key, value] of formData.entries()) {
    answers[key] = parseInt(value, 10);
  }

  try {
    const res = await fetch(`/api/quizzes/${quizId}/submit`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(answers)
    });

    const data = await res.json().catch(() => null);

    if (!res.ok || !data || data.success === false) {
      const msg = (data && data.error) ? data.error : `Submission error (${res.status})`;
      showToast(msg, "error");
      return;
    }

    const resultBox = document.getElementById('quizResultBox');
    if (resultBox) {
      resultBox.style.display = 'block';
      if (data.passed) {
        if (window.soundEngine) window.soundEngine.playSuccessSound();
        resultBox.className = 'card style-success';
        resultBox.innerHTML = `
          <h3 style="color: var(--neon-green);"><i class="fas fa-trophy"></i> QUIZ PASSED! Score: ${data.score}%</h3>
          <p>Congratulations! You earned <strong>+${data.xp_earned} XP</strong>!</p>
        `;
      } else {
        if (window.soundEngine) window.soundEngine.playErrorSound();
        resultBox.className = 'card style-error';
        resultBox.innerHTML = `
          <h3 style="color: var(--neon-red);"><i class="fas fa-times-circle"></i> QUIZ FAILED! Score: ${data.score}%</h3>
          <p>You need at least 70% to pass. Review the lesson and try again!</p>
        `;
      }
      resultBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  } catch (err) {
    console.error("Quiz submission error:", err);
    showToast("Network error submitting quiz answers", "error");
  }
}
