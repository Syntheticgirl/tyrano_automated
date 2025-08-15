// plugin/memo_debugger/main.js
(function () {
  if (TYRANO.kag.config["debugMenu.visible"] !== "true") return;

  if (!window.__memo_debugger) {
    window.__memo_debugger = {
      notes: []
    };
  }

  const { fs, BrowserWindow } = require("electron").remote.require("electron");
  const sf = TYRANO.kag.variable.sf;
  if (!sf.__memo_debugger) sf.__memo_debugger = { notes: [] };

  const $memoUI = $("<div id='memo-debugger'></div>").css({
    position: "fixed",
    bottom: "10px",
    right: "10px",
    width: "300px",
    background: "rgba(0,0,0,0.8)",
    color: "white",
    padding: "10px",
    borderRadius: "8px",
    zIndex: 9999
  });

  const $textarea = $("<textarea rows='4' style='width:100%'></textarea>");
  const $saveBtn = $("<button>メモ保存</button>");
  const $list = $("<ul style='max-height:150px; overflow:auto; font-size:12px'></ul>");

  $saveBtn.on("click", function () {
    const note = $textarea.val().trim();
    if (!note) return;
    const entry = {
      text: note,
      scenario: TYRANO.kag.stat.current_scenario,
      label: TYRANO.kag.stat.current_label,
      line: TYRANO.kag.ftag.current_order_index,
      time: new Date().toLocaleString()
    };
    sf.__memo_debugger.notes.push(entry);
    TYRANO.kag.saveSystemVariable();
    $textarea.val("");
    renderList();
  });

  function renderList() {
    $list.empty();
    sf.__memo_debugger.notes.forEach((n, i) => {
      const $item = $("<li></li>").text(`[${n.time}] ${n.text}`).css({ cursor: "pointer" });
      $item.on("click", function () {
        TYRANO.kag.ftag.startTag("jump", {
          storage: n.scenario,
          target: n.label
        });
      });
      $list.append($item);
    });
  }

  $memoUI.append("<div style='font-weight:bold'>📝 メモ</div>", $textarea, $saveBtn, $list);
  $("body").append($memoUI);
  renderList();
})();