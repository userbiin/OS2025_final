(function ($) {
  $(function () {
    console.log("main.js loaded");
    // 초기 상태
    const pad2 = (n) => String(n).padStart(2, "0");
    const now = new Date();
    const YEAR = now.getFullYear();
    const MONTH = now.getMonth() + 1;
    const DAY = now.getDate();
    const TODAY = `${YEAR}-${pad2(MONTH)}-${pad2(DAY)}`;
    let lastSavedDate = null;
    const yearLabel = document.querySelector(".c-paginator__year");
    if (yearLabel) yearLabel.textContent = String(YEAR);

    const monthText = [
      "January","February","March","April","May","June",
      "July","August","September","October","November","December"
    ];

    let monthEl = $(".c-main");
    let indexMonth = MONTH;


    function defaultEvents(dateStr, name, notes, classTag) {
      const $cell = $(`.c-cal__cel[data-day='${dateStr}']`);
      if (!$cell.length) return;
      $cell.attr("data-name", name || "");
      $cell.attr("data-notes", notes || "");
      $cell.addClass("event");
      if (classTag) $cell.addClass(`event--${classTag}`);
    }


    function fillEventSidebar($cell) {
      $(".c-aside__event").remove();
      const name = $cell.attr("data-name") || "";
      const notes = $cell.attr("data-notes") || "";

      const isImportant = $cell.hasClass("event--important");
      const isBirthday  = $cell.hasClass("event--birthday");
      const isFestivity = $cell.hasClass("event--festivity");
      const isEvent     = $cell.hasClass("event");

      const list = $(".c-aside__eventList");
      const line = (cls) =>
        `<p class="c-aside__event${cls ? " " + cls : ""}">${name} <span> • ${notes}</span></p>`;

      if (isImportant)      return list.append(line("c-aside__event--important"));
      if (isBirthday)       return list.append(line("c-aside__event--birthday"));
      if (isFestivity)      return list.append(line("c-aside__event--festivity"));
      if (isEvent)          return list.append(line(""));
    }

    $(document).on("click", ".c-cal__cel", function () {
      const $this = $(this);
      const dayStr = $this.attr("data-day") || "";
      if (!dayStr) return;

      const dd = dayStr.slice(8);
      const mm = Number(dayStr.slice(5, 7));

      loadDiary(dayStr);
      $(".c-aside__num").text(dd);
      $(".c-aside__month").text(monthText[mm - 1]);

      $(".c-cal__cel").removeClass("isSelected");
      $this.addClass("isSelected");
    });


    (function highlightToday() {
      const $today = $(`.c-cal__cel[data-day='${TODAY}']`);
      if ($today.length) {
        $today.addClass("isToday");
        loadDiary(TODAY);
        $(".c-aside__num").text(pad2(DAY));
        $(".c-aside__month").text(monthText[MONTH - 1]);
        $(".c-cal__cel").removeClass("isSelected");
        $today.addClass("isSelected");
      } else {
        $(".c-aside__num").text(pad2(DAY));
        $(".c-aside__month").text(monthText[MONTH - 1]);
      }
    })();



    const $winCreator = $(".js-event__creator");
    $(".js-event__add").on("click", function (e) {
      e.preventDefault();
      $winCreator.addClass("isVisible");
      $("body").addClass("overlay");
      const $selected = $(".c-cal__cel.isSelected");
      const date = $selected.attr("data-day") || TODAY;
      const dateInput = document.querySelector("input[type='date']");
      if (dateInput) dateInput.value = date;
    });
    $(".js-event__close").on("click", function (e) {
      e.preventDefault();
      $winCreator.removeClass("isVisible");
      $("body").removeClass("overlay");
    });


    function renderEmoji(dateStr, emoji) {
      const cell = document.querySelector(`.c-cal__cel[data-day='${dateStr}']`);
      if (!cell) return;
      let badge = cell.querySelector(".emoji-badge");
      if (!badge) {
        badge = document.createElement("div");
        badge.className = "emoji-badge";
        badge.style.fontSize = "20px";
        badge.style.position = "absolute";
        badge.style.right = "6px";
        badge.style.top = "6px";
        cell.style.position = "relative";
        cell.appendChild(badge);
      }
      badge.textContent = emoji || "";
    }

    function getCurrentYearMonth() {
      const y = document.querySelector(".c-paginator__year")?.textContent?.trim();
      const d = new Date();
      const yyyy = /^\d{4}$/.test(y || "") ? y : String(d.getFullYear());
      const mm = pad2(d.getMonth() + 1);
      return { yyyy, mm };
    }
    async function fetchMonthEmotions(yyyy, mm) {
      try {
        const res = await fetch(`/api/diary?year=${yyyy}&month=${mm}`);
        const data = await res.json();
        if (!data.ok) return;
        (data.items || []).forEach((it) => renderEmoji(it.date, it.emoji));
      } catch (e) {
        console.warn("fetchMonthEmotions error", e);
      }
    }

    (function bindSave() {
      const saveBtn = document.querySelector(".js-event__save");
      const form = document.getElementById("addDiary");
      if (!saveBtn || !form) return;

      saveBtn.addEventListener("click", async (e) => {
        e.preventDefault();

        const inputName  = form.elements["name"]?.value || "";
        const inputDate  = form.elements["date"]?.value || "";
        const inputNotes = form.elements["notes"]?.value || "";
        const inputTag   = form.elements["tags"]?.value || "";

        if (!inputDate) return alert("Select a Date.");
        if (!inputNotes.trim()) return alert("Fill the content.");

        try {
          const res = await fetch("/api/diary", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date: inputDate, text: inputNotes })
          });
          const data = await res.json();
          if (!data.ok) {
            return alert("Save failed: " + (data.error || "unknown"));
          }

          lastSavedDate = data.date;

          renderEmoji(data.date, data.emoji);

          const $cell = $(`.c-cal__cel[data-day='${inputDate}']`);
          if ($cell.length) {
            if (inputName)  $cell.attr("data-name", inputName);
            if (inputNotes) $cell.attr("data-notes", inputNotes);
            $cell.addClass("event");
            if (inputTag)   $cell.addClass(`event--${inputTag}`);
            fillEventSidebar($cell);
            $(".c-aside__num").text(inputDate.slice(8));
            $(".c-aside__month").text(monthText[Number(inputDate.slice(5, 7)) - 1]);
            $(".c-cal__cel").removeClass("isSelected");
            $cell.addClass("isSelected");
          }

          alert(`Saved! ${data.label?.toUpperCase() || ""} ${data.emoji || ""}`);

          $winCreator.removeClass("isVisible");
          $("body").removeClass("overlay");
          form.reset();
        } catch (err) {
          console.error(err);
          alert("Network error");
        }
      });
    })();

        // '상세 보기' 버튼 동작: 현재 선택된 날짜(달력) 기준으로 이동
    (function bindDetailButton() {
      const detailBtn = document.querySelector(".js-event__detail");
      if (!detailBtn) return;

      detailBtn.addEventListener("click", (e) => {
        e.preventDefault();

        let targetDate = "";

        // 1순위: 달력에서 선택된 날짜(.isSelected)
        const $selected = $(".c-cal__cel.isSelected");
        if ($selected.length) {
          targetDate = $selected.attr("data-day") || "";
        }

        // 2순위: 마지막으로 저장한 날짜
        if (!targetDate && lastSavedDate) {
          targetDate = lastSavedDate;
        }

        // 3순위: 그래도 없으면 오늘 날짜
        if (!targetDate) {
          targetDate = TODAY;
        }

        if (!targetDate) {
          alert("상세 보기를 할 날짜를 찾을 수 없습니다.");
          return;
        }

        window.location.href = "/diary/" + targetDate;
      });
    })();



    (function bindDetailButton() {
      const detailBtn = document.querySelector(".js-event__detail");
      if (!detailBtn) return;

      detailBtn.addEventListener("click", (e) => {
        e.preventDefault();

        let targetDate = "";

        // 1순위: 달력에서 선택된 날짜(.isSelected)
        const $selected = $(".c-cal__cel.isSelected");
        if ($selected.length) {
          targetDate = $selected.attr("data-day") || "";
        }

        // 2순위: 마지막으로 저장한 날짜
        if (!targetDate && lastSavedDate) {
          targetDate = lastSavedDate;
        }

        // 3순위: 그래도 없으면 오늘 날짜
        if (!targetDate) {
          targetDate = TODAY;
        }

        if (!targetDate) {
          alert("상세 보기를 할 날짜를 찾을 수 없습니다.");
          return;
        }

        window.location.href = "/diary/" + targetDate;
      });
    })();




    (function initialMonthEmojis() {
      const { yyyy, mm } = getCurrentYearMonth();
      fetchMonthEmotions(yyyy, mm);
    })();


    function moveNext(step, updateIndex) {
      for (let i = 0; i < step; i++) {
        $(".c-main").css({ left: "-=100%" });
        $(".c-paginator__month").css({ left: "-=100%" });
        if (updateIndex) indexMonth += 1;
      }
    }
    function movePrev(step, updateIndex) {
      for (let i = 0; i < step; i++) {
        $(".c-main").css({ left: "+=100%" });
        $(".c-paginator__month").css({ left: "+=100%" });
        if (updateIndex) indexMonth -= 1;
      }
    }

    async function loadDiary(dateStr) {
      try {
        const res = await fetch(`/api/diary/${dateStr}`);
        const data = await res.json();

        if (!data.ok) {
          $(".c-aside__event").remove();
          $(".c-aside__num").text(dateStr.slice(8));
          $(".c-aside__month").text(
            monthText[Number(dateStr.slice(5,7)) - 1]
          );
          return;
        }

        const $cell = $(`.c-cal__cel[data-day='${dateStr}']`);
        if ($cell.length) {
          $cell.attr("data-name", data.label || "Diary");
          $cell.attr("data-notes", data.text || "");
          $cell.addClass("event");
        }

        // 사이드바 갱신
        if ($cell.length) fillEventSidebar($cell);
        $(".c-aside__num").text(dateStr.slice(8));
        $(".c-aside__month").text(
          monthText[Number(dateStr.slice(5,7)) - 1]
        );

      } catch (e) {
        console.warn("loadDiary error", e);
      }
    }


    function buttonsPaginator(buttonId, mainClass, monthClass, goNext, goPrev) {
      $(buttonId).on("click", function (e) {
        e.preventDefault();
        if (goNext) {
          if (indexMonth >= 2) {
            $(mainClass).css({ left: "+=100%" });
            $(monthClass).css({ left: "+=100%" });
            indexMonth -= 1;
            const yy = (document.querySelector(".c-paginator__year")?.textContent || "").trim();
            fetchMonthEmotions(yy, pad2(indexMonth));
          }
          return indexMonth;
        }
        if (goPrev) {
          if (indexMonth <= 11) {
            $(mainClass).css({ left: "-=100%" });
            $(monthClass).css({ left: "-=100%" });
            indexMonth += 1;
            const yy = (document.querySelector(".c-paginator__year")?.textContent || "").trim();
            fetchMonthEmotions(yy, pad2(indexMonth));
          }
          return indexMonth;
        }
      });
    }

    // Paginator 버튼 바인딩
    buttonsPaginator("#next", monthEl, ".c-paginator__month", false, true);
    buttonsPaginator("#prev", monthEl, ".c-paginator__month", true, false);

    $(".c-today__btn").on("click", function (e) {
      e.preventDefault();
      if (MONTH < indexMonth) {
        const step = indexMonth % MONTH;
        movePrev(step, true);
      } else if (MONTH > indexMonth) {
        const step = MONTH - indexMonth;
        moveNext(step, true);
      }
      const yy = (document.querySelector(".c-paginator__year")?.textContent || "").trim();
      fetchMonthEmotions(yy, pad2(indexMonth));

    });
    moveNext(indexMonth - 1, false);
  });
})(jQuery);
