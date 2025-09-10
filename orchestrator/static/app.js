(function(){
  const $ = (s) => document.querySelector(s);

  const promptEl = $("#prompt");
  const sendBtn  = $("#sendBtn");
  const statusEl = $("#status");
  const respEl   = $("#response");

  const agentEls = {
    coder:  $("#agent-coder"),
    analyst:$("#agent-analyst"),
    travel: $("#agent-travel"),
  };

  const statusEls = {
    coder:  $("#status-coder"),
    analyst:$("#status-analyst"),
    travel: $("#status-travel"),
  };

  const selectionInfo = $("#selection-info");
  const selectionText = $("#selection-text");

  const agentNames = {
    coder: "Coder (ソフトウェアエンジニア)",
    analyst: "Analyst (データアナリスト)",
    travel: "Travel (旅行プランナー)"
  };

  function clearHighlights(){
    Object.values(agentEls).forEach(el =>
      el.classList.remove(
        "selected",
        "selected-coder",
        "selected-analyst",
        "selected-travel"
      )
    );
    Object.values(statusEls).forEach(el => el.style.display = 'none');
    
    selectionInfo.classList.remove("active", "active-coder", "active-analyst", "active-travel");
    selectionText.textContent = "エージェントが選択されると、ここに表示されます";
  }

  async function ask(){
    const prompt = (promptEl.value || "").trim();
    if(!prompt){
      statusEl.textContent = "プロンプトを入力してください。";
      return;
    }

    clearHighlights();
    respEl.textContent = "";
    sendBtn.disabled = true;
    statusEl.textContent = "Thinking...";

    try{
      const r = await fetch("/api/ask", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ prompt })
      });
      const data = await r.json();

      if(!r.ok){
        throw new Error(data.error || `HTTP ${r.status}`);
      }

      // data.selected: "coder" | "analyst" | "travel" | "none"
      console.log("API Response:", data); // デバッグログ
      
      if(data.selected && agentEls[data.selected]){
        agentEls[data.selected].classList.add("selected", `selected-${data.selected}`);
        if(statusEls[data.selected]){
          statusEls[data.selected].style.display = 'block';
        }
        
        // Update selection info
        selectionInfo.classList.add("active", `active-${data.selected}`);
        selectionText.textContent = `✓ ${agentNames[data.selected]} が選択されて回答しました`;
      } else if(data.selected === "none") {
        // Show general response info
        selectionInfo.classList.add("active");
        selectionText.textContent = "✓ 汎用エージェントが応答しました";
      } else {
        // エラーケース
        selectionInfo.classList.add("active");
        selectionText.textContent = `⚠️ 不明なエージェント (${data.selected}) が応答しました`;
      } // "none" の場合はハイライトなし

      respEl.textContent = data.response || "(no content)";
      statusEl.textContent = "Done.";
    }catch(err){
      console.error(err);
      statusEl.textContent = "Error.";
      respEl.textContent = String(err);
    }finally{
      sendBtn.disabled = false;
    }
  }

  sendBtn.addEventListener("click", ask);
  promptEl.addEventListener("keydown", (e)=>{
    if((e.ctrlKey || e.metaKey) && e.key === "Enter"){
      ask();
    }
  });
})();
