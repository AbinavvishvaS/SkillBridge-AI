/**
 * SkillBridge AI - Super Edition v2.5 Interactive Engine
 * 
 * Includes:
 * 1. Global Floating AI Doubt Assistant Drawer
 * 2. Multi-Dimensional Proficiency Rating Pills
 * 3. Real-Time "What-If" Skill Simulator & SVG Radar Engine
 * 4. Interactive Quiz Handlers for Doubts & Confidence
 * 5. Code Copying and UI Feedback
 */

document.addEventListener("DOMContentLoaded", () => {
  /* ==========================================================================
     1. Global Floating AI Doubt Assistant Drawer
     ========================================================================== */
  const openDoubtDrawerBtn = document.getElementById("openDoubtDrawerBtn");
  const closeDoubtDrawerBtn = document.getElementById("closeDoubtDrawerBtn");
  const drawerBackdrop = document.getElementById("drawerBackdrop");
  const doubtDrawer = document.getElementById("doubtDrawer");
  const drawerDoubtForm = document.getElementById("drawerDoubtForm");
  const drawerLoading = document.getElementById("drawerLoading");
  const drawerResult = document.getElementById("drawerResult");
  const drawerClearAnotherBtn = document.getElementById("drawerClearAnotherBtn");

  const openDrawer = () => {
    if (doubtDrawer && drawerBackdrop) {
      doubtDrawer.classList.add("open");
      drawerBackdrop.classList.add("open");
      doubtDrawer.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      setTimeout(() => {
        const queryInput = document.getElementById("drawerQueryInput");
        if (queryInput) queryInput.focus();
      }, 200);
    }
  };

  const closeDrawer = () => {
    if (doubtDrawer && drawerBackdrop) {
      doubtDrawer.classList.remove("open");
      drawerBackdrop.classList.remove("open");
      doubtDrawer.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }
  };

  if (openDoubtDrawerBtn) openDoubtDrawerBtn.addEventListener("click", openDrawer);
  if (closeDoubtDrawerBtn) closeDoubtDrawerBtn.addEventListener("click", closeDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener("click", closeDrawer);

  // Keyboard shortcut: Escape closes drawer
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && doubtDrawer && doubtDrawer.classList.contains("open")) {
      closeDrawer();
    }
  });

  // Drawer Form Submission via REST API
  if (drawerDoubtForm) {
    drawerDoubtForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const queryInput = document.getElementById("drawerQueryInput");
      const catSelect = document.getElementById("drawerCatSelect");
      const submitBtn = document.getElementById("drawerSubmitBtn");

      if (!queryInput || !queryInput.value.trim()) return;

      const question = queryInput.value.trim();
      const category = catSelect ? catSelect.value : "General";

      if (submitBtn) submitBtn.disabled = true;
      if (drawerLoading) drawerLoading.style.display = "block";
      if (drawerResult) drawerResult.style.display = "none";

      try {
        const res = await fetch("/api/resolve-doubt", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question, category })
        });
        const data = await res.json();

        if (drawerLoading) drawerLoading.style.display = "none";
        if (submitBtn) submitBtn.disabled = false;

        if (res.ok && data.status === "success") {
          const r = data.result;
          document.getElementById("drawerResCat").textContent = r.category;
          document.getElementById("drawerResScore").textContent = `🛡️ ${r.accuracy_score}% Accuracy`;
          document.getElementById("drawerResQ").textContent = r.question;
          document.getElementById("drawerResShort").textContent = r.short_answer;
          document.getElementById("drawerResDetail").textContent = r.detailed_explanation;

          const codeWrap = document.getElementById("drawerCodeWrap");
          const codeEl = document.getElementById("drawerResCode");
          if (r.code_example && r.code_example.trim()) {
            codeEl.textContent = r.code_example;
            codeWrap.style.display = "block";
          } else {
            codeWrap.style.display = "none";
          }

          const pitfallWrap = document.getElementById("drawerPitfallWrap");
          const pitfallEl = document.getElementById("drawerResPitfall");
          if (r.common_pitfall && r.common_pitfall.trim()) {
            pitfallEl.textContent = r.common_pitfall;
            pitfallWrap.style.display = "flex";
          } else {
            pitfallWrap.style.display = "none";
          }

          if (drawerResult) drawerResult.style.display = "block";

          // Update header points if element exists
          const pointsPills = document.querySelectorAll(".pill-val, .profile-pts-tag");
          pointsPills.forEach(el => {
            const current = parseInt(el.textContent) || 0;
            el.textContent = current + 15;
          });
        } else {
          alert(data.message || "Failed to resolve doubt. Please try again.");
        }
      } catch (err) {
        if (drawerLoading) drawerLoading.style.display = "none";
        if (submitBtn) submitBtn.disabled = false;
        alert("Network error while resolving doubt. Please check your connection.");
      }
    });
  }

  if (drawerClearAnotherBtn) {
    drawerClearAnotherBtn.addEventListener("click", () => {
      const queryInput = document.getElementById("drawerQueryInput");
      if (queryInput) {
        queryInput.value = "";
        queryInput.focus();
      }
      if (drawerResult) drawerResult.style.display = "none";
    });
  }

  /* ==========================================================================
     2. Interactive Self-Check Quizzes (Doubts Vault)
     ========================================================================== */
  const quizForms = document.querySelectorAll(".quiz-form");
  quizForms.forEach(form => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const doubtId = form.getAttribute("data-doubt-id");
      const selected = form.querySelector(`input[name="quiz_${doubtId}"]:checked`);
      const feedbackEl = document.getElementById(`quiz-feedback-${doubtId}`);
      if (!selected) {
        if (feedbackEl) {
          feedbackEl.className = "quiz-feedback error";
          feedbackEl.textContent = "Please select an answer choice first!";
          feedbackEl.style.display = "block";
        }
        return;
      }

      const isCorrect = selected.getAttribute("data-correct") === "true";
      const explanation = selected.getAttribute("data-explanation") || "";

      if (feedbackEl) {
        if (isCorrect) {
          feedbackEl.className = "quiz-feedback success";
          feedbackEl.innerHTML = `<strong>✓ Correct!</strong> ${explanation}`;
        } else {
          feedbackEl.className = "quiz-feedback error";
          feedbackEl.innerHTML = `<strong>✕ Incorrect.</strong> ${explanation}`;
        }
        feedbackEl.style.display = "block";
      }
    });
  });
});

/* ==========================================================================
   3. Multi-Skill Proficiency Picker Toggle
   ========================================================================== */
function toggleProficiencyPicker(checkbox, skillName) {
  const container = document.getElementById(`prof-picker-${skillName}`);
  if (!container) return;
  if (checkbox.checked) {
    container.style.display = "flex";
  } else {
    container.style.display = "none";
  }
}

/* ==========================================================================
   4. Real-Time "What-If" Simulator Toggle
   ========================================================================== */
async function simulateSkillToggle(btn, skillName, targetCareer) {
  const isAcquired = btn.getAttribute("data-acquired") === "true";
  const newAcquired = !isAcquired;

  // Optimistic UI state toggle
  btn.setAttribute("data-acquired", newAcquired ? "true" : "false");
  btn.classList.toggle("acquired", newAcquired);

  const statusTag = document.getElementById(`sim-status-${skillName}`);
  if (statusTag) {
    statusTag.textContent = newAcquired ? "Acquired (Simulated)" : "Skill Gap";
    statusTag.className = `sim-skill-status ${newAcquired ? "acquired-tag" : "gap-tag"}`;
  }

  // Gather current acquired skills from simulator chips
  const allChips = document.querySelectorAll(".sim-chip-btn");
  const simulatedSkills = [];
  allChips.forEach(chip => {
    if (chip.getAttribute("data-acquired") === "true") {
      simulatedSkills.push(chip.getAttribute("data-skill"));
    }
  });

  try {
    const res = await fetch("/api/simulate-skill", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        career: targetCareer,
        acquired_skills: simulatedSkills
      })
    });
    const data = await res.json();
    if (res.ok && data.status === "success") {
      // Update Simulator Metrics
      const matchPctEl = document.getElementById("simMatchPct");
      const gapCountEl = document.getElementById("simGapCount");
      const hoursEl = document.getElementById("simHours");
      const deltaEl = document.getElementById("simDeltaBadge");

      if (matchPctEl) matchPctEl.textContent = `${data.match_percentage}%`;
      if (gapCountEl) gapCountEl.textContent = data.gap_count;
      if (hoursEl) hoursEl.textContent = `${data.estimated_study_hours} hrs`;

      if (deltaEl) {
        if (data.percentage_delta > 0) {
          deltaEl.textContent = `+${data.percentage_delta}% readiness boost`;
          deltaEl.className = "sim-delta positive";
        } else if (data.percentage_delta < 0) {
          deltaEl.textContent = `${data.percentage_delta}% drop`;
          deltaEl.className = "sim-delta negative";
        } else {
          deltaEl.textContent = "Baseline readiness";
          deltaEl.className = "sim-delta neutral";
        }
      }

      // Update SVG Spider Radar Chart in Real Time
      updateSvgRadar(data.competency_radar);
    }
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

/* ==========================================================================
   5. Dynamic SVG Spider Radar Updater
   ========================================================================== */
function updateSvgRadar(radarScores) {
  if (!radarScores) return;
  const poly = document.getElementById("svgRadarPolygon") || document.getElementById("radarDataPolygon");
  if (!poly) return;

  const dims = ["Foundational", "Execution", "Architecture", "Tooling", "Problem Solving"];
  const cx = 150, cy = 150, maxR = 100;
  const numAxes = dims.length;
  const points = [];

  dims.forEach((d, i) => {
    const score = radarScores[d] || 0;
    const r = (score / 100) * maxR;
    const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`);

    const dot = document.getElementById(`radarDot-${i}`);
    if (dot) {
      dot.setAttribute("cx", x.toFixed(1));
      dot.setAttribute("cy", y.toFixed(1));
    }
  });

  poly.setAttribute("points", points.join(" "));
}

/* ==========================================================================
   6. Global Floating Doubt Launcher for Specific Skill
   ========================================================================== */
function launchDoubtForSkill(skillName, domain = "General") {
  const openDoubtDrawerBtn = document.getElementById("openDoubtDrawerBtn");
  if (openDoubtDrawerBtn) openDoubtDrawerBtn.click();

  setTimeout(() => {
    const queryInput = document.getElementById("drawerQueryInput");
    const catSelect = document.getElementById("drawerCatSelect");
    if (queryInput) {
      queryInput.value = `How do I master ${skillName} and what are the most common interview pitfalls?`;
      queryInput.focus();
    }
    if (catSelect && domain) {
      for (let opt of catSelect.options) {
        if (opt.value.toLowerCase().includes(domain.toLowerCase())) {
          catSelect.value = opt.value;
          break;
        }
      }
    }
  }, 250);
}

/* ==========================================================================
   7. Code Copy Helper
   ========================================================================== */
function copyCode(btn) {
  const wrapper = btn.closest(".code-wrapper");
  if (!wrapper) return;
  const codeEl = wrapper.querySelector("code");
  if (!codeEl) return;

  navigator.clipboard.writeText(codeEl.innerText).then(() => {
    const orig = btn.innerText;
    btn.innerText = "✓ Copied!";
    btn.classList.add("copied");
    setTimeout(() => {
      btn.innerText = orig;
      btn.classList.remove("copied");
    }, 2000);
  }).catch(() => {
    btn.innerText = "Error";
  });
}
