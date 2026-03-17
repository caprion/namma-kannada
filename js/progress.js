// Progress — localStorage-backed, no backend needed.
// Schema: { stage_1: { completed: 12 }, stage_2: { completed: 0 }, ... }

const Progress = (function () {
  const KEY = 'namma_progress';

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch {
      return {};
    }
  }

  function save(data) {
    localStorage.setItem(KEY, JSON.stringify(data));
  }

  function getStageProgress(stageId) {
    const data = load();
    return data[`stage_${stageId}`] || { completed: 0 };
  }

  function setStageProgress(stageId, completed) {
    const data = load();
    data[`stage_${stageId}`] = { completed };
    save(data);
  }

  function isStageUnlocked(stageId, allStages) {
    if (stageId === 1) return true;
    const prevStage = allStages.find(s => s.id === stageId - 1);
    if (!prevStage || prevStage.sentences.length === 0) return true; // unlock if prev has no content yet
    const prevProgress = getStageProgress(stageId - 1);
    return prevProgress.completed >= prevStage.sentences.length;
  }

  function reset() {
    localStorage.removeItem(KEY);
  }

  return { getStageProgress, setStageProgress, isStageUnlocked, reset };
})();
