var myModal = new bootstrap.Modal(document.getElementById("myModal"), {
  backdrop: "static",
  keyboard: true,
  focus: true,
});

myModal.show();

$(function () {
  var ctx = document.getElementById("myChart").getContext("2d");
  var ChartDate = [];
  var ChartData = [];
  var ChartData1 = [];
  var d;
  //'rgba(255, 99, 132, 0.2)',
  //'rgba(54, 162, 235, 0.2)',
  //'rgba(255, 206, 86, 0.2)',
  //'rgba(75, 192, 192, 0.2)',
  //'rgba(153, 102, 255, 0.2)',
  //'rgba(255, 159, 64, 0.2)'
  var chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ChartDate,
      datasets: [
        {
          label: "獲利",
          data: ChartData,
          backgroundColor: ["rgba(153, 102, 255, 0.2)"],
          borderColor: ["rgba(153, 102, 255, 0.2)"],
          borderWidth: 1,
        },
        {
          label: "累積獲利",
          data: ChartData1,
          borderColor: ["rgba(255, 159, 64, 0.2)"],
          backgroundColor: ["rgba(255, 159, 64, 1)"],
          type: "line",
          order: 0,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  var myTables = $("#datatable").dataTable({
    paging: true,
    ordering: true,
    language: {
      info: "",
      paginate: {
        previous: "＜",
        next: "＞",
      },
    },
    //"update": true,
    destroy: true,
    retrieve: true,
  });

  $("#submit").on("click", function () {
    myModal.show();
    reques();
    $("html, body").animate(
      { scrollTop: $("#myChart").offset().top - 210 },
      1000
    );
  });

  function reques() {
    let data = {
      stock: $("#stock").val(),
      KbarsMinutes: $("#KbarsMinutes").val(),
      KbarsNewHigh: $("#KbarsNewHigh").val(),
      StopLoss: $("#StopLoss").val(),
    };

    axios
      .post("/api/get_data", Qs.stringify(data))
      .then((res) => {
        let response = res["data"];
        d = response["data"];
        clears();

        myTables.fnClearTable();
        myTables.fnDestroy();
        $("#datatable").find("tbody").append("");

        d["售出時間"].forEach(function (val, i) {
          ChartDate.push(d["售出日期"][i]);
          ChartData.push(d["獲利"][i]);
          ChartData1.push(d["累積獲利"][i]);
          chart.update();

          var text = "<tr>";
          text +=
            `<td class="details-control d-table-cell d-lg-none">` +
            `<i class="bi bi-plus-circle-fill"></i>` +
            `</td>`;
          text +=
            `<td class="d-none d-lg-table-cell">` + d["買進日期"][i] + "</td>";
          text +=
            `<td class="d-none d-lg-table-cell">` + d["買進時間"][i] + "</td>";
          text += "<td>" + d["買進價格"][i] + "</td>";
          text +=
            `<td class="d-none d-lg-table-cell">` + d["售出日期"][i] + "</td>";
          text +=
            `<td class="d-none d-lg-table-cell">` + d["售出時間"][i] + "</td>";
          text += "<td>" + d["售出價格"][i] + "</td>";
          text +=
            `<td class="d-none d-lg-table-cell">` + d["數量"][i] + "</td>";
          if (d["獲利"][i] > 0) {
            text += `<td class="text-danger">` + d["獲利"][i] + `</td>`;
          } else {
            text += `<td class="text-success">` + d["獲利"][i] + `</td>`;
          }
          text += "</tr>";
          $("#datatable").find("tbody").append(text);
        });
        myTables = $("#datatable").dataTable({
          paging: true,
          ordering: true,
          language: {
            info: "",
            paginate: {
              previous: "＜",
              next: "＞",
            },
          },
          destroy: true,
          retrieve: true,
        });

        $("#Total_Trade").html(response["交易次數"]);
        $("#Total_Profit").html(response["總損益"]);
        $("#Avg_Profit").html(Math.floor(response["平均損益"] * 100) / 100);
        $("#Win_Rate").html(response["勝率"]);
        $("#Profit_Factor").html(response["獲利因子"]);
        $("#Win_Loss_Rate").html(response["賺賠比"]);
        $("#MDD").html(response["最大資金回落"]);
        $("#Sharpe_Ratio").html(response["夏普比率"]);
        $("#Over_5_Millions").html(response["是否超額交易"]);

        setTimeout(function () {
          myModal.hide();
        }, 400);
      })
      .catch((err) => {
        setTimeout(function () {
          myModal.hide();
        }, 400);
        console.error(err);
      });
  }
  $("#datatable tbody").on("click", "td.details-control", function () {
    let tr = $(this).closest("tr");
    let td = tr.children();

    if (tr.hasClass("show")) {
      $(this).html(`<i class="bi bi-plus-circle-fill"></i>`);
      tr.removeClass("show");
      tr.next().remove();
    } else {
      $(this).html(`<i class="bi bi-dash-circle-fill"></i>`);
      tr.addClass("show");
      let text =
        `<td colspan="9"><table class="table" border="0" style="width:100%;padding-left:50px;">` +
        `<tr><td>買進日期</td><td>` +
        td[1].innerHTML +
        " " +
        td[2].innerHTML +
        `</td></tr>` +
        `<tr><td>售出日期</td><td>` +
        td[4].innerHTML +
        " " +
        td[2].innerHTML +
        `</td></tr>` +
        `<tr><td>數量</td><td>` +
        td[7].innerHTML +
        `</td></tr>` +
        `</table></td>`;
      let add = $(this).parent("tr");
      add.after(text);
    }
  });
  $(".RevenueYear a").on("click", function () {
    $(".RevenueYear a").removeClass("active");
    $(this).addClass("active");
    let year = $(this).html();
    clears();
    d["售出日期"].forEach(function (val, i) {
      if (val.substr(0, 4) == year) {
        ChartDate.push(d["售出日期"][i]);
        ChartData.push(d["獲利"][i]);
        ChartData1.push(d["累積獲利"][i]);
        chart.update();
      } else if (year == "ALL") {
        ChartDate.push(d["售出日期"][i]);
        ChartData.push(d["獲利"][i]);
        ChartData1.push(d["累積獲利"][i]);
        chart.update();
      }
    });
  });

  function clears() {
    var x = ChartDate.length;
    for (var i = 0; i <= x; i++) {
      ChartDate.pop();
      ChartData.pop();
      ChartData1.pop();
    }
    //$('#tbody').html();
    chart.update();
  }
  setTimeout(function () {
    myModal.hide();
  }, 500);
  reques();
});
