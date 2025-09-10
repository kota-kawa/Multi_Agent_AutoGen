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

  function clearHighlights(){
    Object.values(agentEls).forEach(el =>
      el.classList.remove(
        "selected",
        "selected-coder",
        "selected-analyst",
        "selected-travel"
      )
    );
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
      if(data.selected && agentEls[data.selected]){
        agentEls[data.selected].classList.add("selected", `selected-${data.selected}`);
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
