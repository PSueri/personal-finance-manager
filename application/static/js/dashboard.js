"use strict";

const dashboardData = JSON.parse(
    document.getElementById("dashboard-data").textContent
);

const euroFormatter = new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
});

const categoryPalette = [
    "#5DA5DA",
    "#FAA43A",
    "#60BD68",
    "#E16851",
    "#FF66B2",
    "#FB8267",
    "#B276B2",
    "#8C9DA8",
];

function chartOptions(title, chartType, values) {
    const options = {
        responsive: true,
        title: {
            display: true,
            text: title,
            fontSize: 20,
        },
        legend: {
            display: true,
            position: "right",
            labels: {
                fontColor: "gray",
            },
        },
        tooltips: {
            callbacks: {
                label: function (tooltipItem, chartData) {
                    const dataset =
                        chartData.datasets[tooltipItem.datasetIndex];

                    const label = chartType === "pie"
                        ? chartData.labels[tooltipItem.index]
                        : dataset.label;

                    const value = dataset.data[tooltipItem.index];

                    return `${label}: ${euroFormatter.format(value)}`;
                },
            },
        },
    };

    if (chartType !== "pie") {
        options.scales = {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    min: Math.min(0, ...values),
                    callback: function (value) {
                        return euroFormatter.format(value);
                    },
                },
            }],
        };
    }

    return options;
}

function createCategoryPair(
    barId,
    pieId,
    labels,
    values,
    title,
    datasetLabel
) {
    const colors = labels.map(
        (_, index) => categoryPalette[index % categoryPalette.length]
    );

    for (const [chartType, canvasId] of [
        ["bar", barId],
        ["pie", pieId],
    ]) {
        new Chart(document.getElementById(canvasId), {
            type: chartType,
            data: {
                labels: labels,
                datasets: [{
                    label: datasetLabel,
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 1,
                    hoverBorderColor: "black",
                    hoverBorderWidth: 2,
                }],
            },
            options: chartOptions(title, chartType, values),
        });
    }
}

new Chart(document.getElementById("income_vs_expense"), {
    type: "bar",
    data: {
        labels: dashboardData.labels,
        datasets: [
            {
                label: "Income",
                data: dashboardData.income_month,
                backgroundColor: "#79EA86",
                borderWidth: 1,
            },
            {
                label: "Expenses",
                data: dashboardData.expense_month,
                backgroundColor: "#E16851",
                borderWidth: 1,
            },
        ],
    },
    options: chartOptions(
        "Income vs Expenses",
        "bar",
        [
            ...dashboardData.income_month,
            ...dashboardData.expense_month,
        ]
    ),
});

new Chart(document.getElementById("netflow"), {
    type: "line",
    data: {
        labels: dashboardData.labels,
        datasets: [{
            label: "Net Cash Flow",
            data: dashboardData.netflow_month,
            fill: false,
            borderColor: "#79EA86",
            lineTension: 0.1,
        }],
    },
    options: chartOptions(
        "Net Cash Flow",
        "line",
        dashboardData.netflow_month
    ),
});

createCategoryPair(
    "expenses_year_vs_category",
    "expense_year_pie",
    dashboardData.category_expenses_year_labels,
    dashboardData.category_expenses_year_values,
    "Annual Expenses by Category",
    "Expenses"
);

createCategoryPair(
    "expenses_vs_category",
    "expense_pie",
    dashboardData.category_expenses_labels,
    dashboardData.category_expenses_values,
    "Monthly Expenses by Category",
    "Expenses"
);

createCategoryPair(
    "incomes_year_vs_category",
    "income_year_pie",
    dashboardData.category_incomes_year_labels,
    dashboardData.category_incomes_year_values,
    "Annual Income by Subcategory",
    "Income"
);

createCategoryPair(
    "incomes_vs_category",
    "income_pie",
    dashboardData.category_incomes_labels,
    dashboardData.category_incomes_values,
    "Monthly Income by Subcategory",
    "Income"
);