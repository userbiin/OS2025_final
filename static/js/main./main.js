//global variables
var monthEl = $(".c-main");
var dataCel = $(".c-cal__cel");
var dateObj = new Date();
var month = dateObj.getUTCMonth() + 1;
var day = dateObj.getUTCDate();
var year = dateObj.getUTCFullYear();
var monthText = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
];
var indexMonth = month;
var todayBtn = $(".c-today__btn");
var addBtn = $(".js-event__add");
var saveBtn = $(".js-event__save");
var closeBtn = $(".js-event__close");
var winCreator = $(".js-event__creator");
var inputDate = $(this).data();
today = year + "-" + month + "-" + day;


// ------ set default events -------
function defaultEvents(dataDay,dataName,dataNotes,classTag){
  var date = $('*[data-day='+dataDay+']');
  date.attr("data-name", dataName);
  date.attr("data-notes", dataNotes);
  date.addClass("event");
  date.addClass("event--" + classTag);
}

defaultEvents(today, 'YEAH!','Today is your day','important');
defaultEvents('2022-12-25', 'MERRY CHRISTMAS','A lot of gift!!!!','festivity');
defaultEvents('2022-05-04', "LUCA'S BIRTHDAY",'Another gifts...?','birthday');
defaultEvents('2022-03-03', "MY LADY'S BIRTHDAY",'A lot of money to spent!!!!','birthday');


// ------ functions control -------

//button of the current day
todayBtn.on("click", function() {
  if (month < indexMonth) {
    var step = indexMonth % month;
    movePrev(step, true);
  } else if (month > indexMonth) {
    var step = month - indexMonth;
    moveNext(step, true);
  }
});

//higlight the cel of current day
dataCel.each(function() {
  if ($(this).data("day") === today) {
    $(this).addClass("isToday");
    fillEventSidebar($(this));
  }
});

//window event creator
addBtn.on("click", function() {
  winCreator.addClass("isVisible");
  $("body").addClass("overlay");
  dataCel.each(function() {
    if ($(this).hasClass("isSelected")) {
      today = $(this).data("day");
      document.querySelector('input[type="date"]').value = today;
    } else {
      document.querySelector('input[type="date"]').value = today;
    }
  });
});
closeBtn.on("click", function() {
  winCreator.removeClass("isVisible");
  $("body").removeClass("overlay");
});
saveBtn.on("click", function() {
  var inputName = $("input[name=name]").val();
  var inputDate = $("input[name=date]").val();
  var inputNotes = $("textarea[name=notes]").val();
  var inputTag = $("select[name=tags]")
    .find(":selected")
    .text();

  dataCel.each(function() {
    if ($(this).data("day") === inputDate) {
      if (inputName != null) {
        $(this).attr("data-name", inputName);
      }
      if (inputNotes != null) {
        $(this).attr("data-notes", inputNotes);
      }
      $(this).addClass("event");
      if (inputTag != null) {
        $(this).addClass("event--" + inputTag);
      }
      fillEventSidebar($(this));
    }
  });

  winCreator.removeClass("isVisible");
  $("body").removeClass("overlay");
  $("#addEvent")[0].reset();
});

//fill sidebar event info
function fillEventSidebar(self) {
  $(".c-aside__event").remove();
  var thisName = self.attr("data-name");
  var thisNotes = self.attr("data-notes");
  var thisImportant = self.hasClass("event--important");
  var thisBirthday = self.hasClass("event--birthday");
  var thisFestivity = self.hasClass("event--festivity");
  var thisEvent = self.hasClass("event");
  
  switch (true) {
    case thisImportant:
      $(".c-aside__eventList").append(
        "<p class='c-aside__event c-aside__event--important'>" +
        thisName +
        " <span> • " +
        thisNotes +
        "</span></p>"
      );
      break;
    case thisBirthday:
      $(".c-aside__eventList").append(
        "<p class='c-aside__event c-aside__event--birthday'>" +
        thisName +
        " <span> • " +
        thisNotes +
        "</span></p>"
      );
      break;
    case thisFestivity:
      $(".c-aside__eventList").append(
        "<p class='c-aside__event c-aside__event--festivity'>" +
        thisName +
        " <span> • " +
        thisNotes +
        "</span></p>"
      );
      break;
    case thisEvent:
      $(".c-aside__eventList").append(
        "<p class='c-aside__event'>" +
        thisName +
        " <span> • " +
        thisNotes +
        "</span></p>"
      );
      break;
   }
};
dataCel.on("click", function() {
  var thisEl = $(this);
  var thisDay = $(this)
  .attr("data-day")
  .slice(8);
  var thisMonth = $(this)
  .attr("data-day")
  .slice(5, 7);

  fillEventSidebar($(this));

  $(".c-aside__num").text(thisDay);
  $(".c-aside__month").text(monthText[thisMonth - 1]);

  dataCel.removeClass("isSelected");
  thisEl.addClass("isSelected");

});

//function for move the months
function moveNext(fakeClick, indexNext) {
  for (var i = 0; i < fakeClick; i++) {
    $(".c-main").css({
      left: "-=100%"
    });
    $(".c-paginator__month").css({
      left: "-=100%"
    });
    switch (true) {
      case indexNext:
        indexMonth += 1;
        break;
    }
  }
}
function movePrev(fakeClick, indexPrev) {
  for (var i = 0; i < fakeClick; i++) {
    $(".c-main").css({
      left: "+=100%"
    });
    $(".c-paginator__month").css({
      left: "+=100%"
    });
    switch (true) {
      case indexPrev:
        indexMonth -= 1;
        break;
    }
  }
}

//months paginator
function buttonsPaginator(buttonId, mainClass, monthClass, next, prev) {
  switch (true) {
    case next:
      $(buttonId).on("click", function() {
        if (indexMonth >= 2) {
          $(mainClass).css({
            left: "+=100%"
          });
          $(monthClass).css({
            left: "+=100%"
          });
          indexMonth -= 1;
        }
        return indexMonth;
      });
      break;
    case prev:
      $(buttonId).on("click", function() {
        if (indexMonth <= 11) {
          $(mainClass).css({
            left: "-=100%"
          });
          $(monthClass).css({
            left: "-=100%"
          });
          indexMonth += 1;
        }
        return indexMonth;
      });
      break;
  }
}

buttonsPaginator("#next", monthEl, ".c-paginator__month", false, true);
buttonsPaginator("#prev", monthEl, ".c-paginator__month", true, false);

//launch function to set the current month
moveNext(indexMonth - 1, false);

//fill the sidebar with current day
$(".c-aside__num").text(day);
$(".c-aside__month").text(monthText[month - 1]);


// static/js/main.js

// YYYY, MM을 얻는 헬퍼
function getCurrentYearMonth() {
  const y = document.querySelector(".c-paginator__year")?.textContent?.trim();
  // 현재 보이는 month index를 계산하는 로직이 따로 있다면 거기에 맞춰 조정.
  // 여기서는 실제 브라우저 날짜 기준으로 단순화:
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const yyyy = y && /^\d{4}$/.test(y) ? y : String(d.getFullYear());
  return { yyyy, mm };
}

// 셀에 이모지 렌더
function renderEmoji(dateStr, emoji) {
  const cell = document.querySelector(`.c-cal__cel[data-day='${dateStr}']`);
  if (!cell) return;
  // 이미 존재하면 교체
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
  badge.textContent = emoji;
}

// 월 데이터 불러오기
async function fetchMonthEmotions(yyyy, mm) {
  const res = await fetch(`/api/diary?year=${yyyy}&month=${mm}`);
  const data = await res.json();
  if (!data.ok) return;
  data.items.forEach(item => {
    renderEmoji(item.date, item.emoji);
  });
}

// SAVE 버튼 연결
document.addEventListener("DOMContentLoaded", () => {
  const saveBtn = document.querySelector(".js-event__save");
  const form = document.getElementById("addEvent");

  if (saveBtn && form) {
    saveBtn.addEventListener("click", async () => {
      const date = form.elements["date"].value;   // YYYY-MM-DD
      const notes = form.elements["notes"].value; // 일기 텍스트

      if (!date) {
        alert("날짜를 선택해 주세요.");
        return;
      }
      if (!notes || !notes.trim()) {
        alert("일기 내용을 입력해 주세요.");
        return;
      }

      try {
        const res = await fetch("/api/diary", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ date, text: notes })
        });
        const data = await res.json();
        if (data.ok) {
          renderEmoji(data.date, data.emoji);
          alert(`Saved! ${data.label.toUpperCase()} ${data.emoji}`);
        } else {
          alert("Save failed: " + (data.error || "unknown"));
        }
      } catch (e) {
        console.error(e);
        alert("Network error");
      }
    });
  }

  // 초기 로드 시 현재 월 이모지 채우기
  const { yyyy, mm } = getCurrentYearMonth();
  fetchMonthEmotions(yyyy, mm);
});
