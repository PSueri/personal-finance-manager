"use strict";

const dashboardData = JSON.parse(
    document.getElementById("dashboard-data").textContent
);

const {
    income_month,
    expense_month,
    netflow_month,
    labels,
    category_expenses_values,
    category_expenses_labels,
    category_expenses_year_values,
    category_expenses_year_labels,
    category_incomes_values,
    category_incomes_labels,
    category_incomes_year_values,
    category_incomes_year_labels,
} = dashboardData;

function getAxisMinimum(values) {
    return Math.min(0, ...values);
}

Chart.scaleService.updateScaleDefaults('linear', {
        ticks: {
            min: 0
        }
});

let income_vs_expense_chart = new Chart(document.getElementById("income_vs_expense"), {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: "Incomes",
            data: income_month,
            backgroundColor: '#79EA86',
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(154, 245, 140)',
            pointHoverRadius: 5
        },
        {
            label: "Expenses",
            data: expense_month,
            backgroundColor: '#E16851',
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(255, 100, 100)',
            pointHoverRadius: 5
        }],
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                min: 0,
            }
        },
        title: {
            display: true,
            text: "Incomes vs Expenses",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

Chart.scaleService.updateScaleDefaults('linear', {
        ticks: {

        }
});

new Chart(document.getElementById("netflow"), {
    type: "line",
    data: {
        labels: labels,
        datasets: [{
            label: "NetFlow",
            data: netflow_month,
            fill: false,
            borderColor: "rgb(121,234,134)",
            lineTension: 0.1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                min: getAxisMinimum(netflow_month)
            }
        }
    }
});

Chart.scaleService.updateScaleDefaults('linear', {
        ticks: {
            min: 0
        }
});

let expenses_year_vs_category_chart = new Chart(document.getElementById("expenses_year_vs_category"), {
    type: 'bar',
    data: {
        labels: category_expenses_year_labels,
        datasets: [{
            label: "Categories Of Expenses",
            data: category_expenses_year_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#60BD68',
                '#E16851','#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                min: getAxisMinimum(category_expenses_year_values),
            }
        },
        title: {
            display: true,
                text: "Expenses per Categories in selected year",
                    fontSize: 20,
        },
        legend: {
            position: "right",
                labels: {
                fontColor: "gray"
                },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

let expense_year_pie_chart = new Chart(document.getElementById("expense_year_pie"), {
    type: 'pie',
    data: {
        labels: category_expenses_year_labels,
        datasets: [{
            label: "Expenses",
            data: category_expenses_year_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#60BD68',
                '#E16851','#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
            title: {
                display: true,
                text: "Expenses per Categories in selected year",
                fontSize: 20,
            },
            legend: {
                position: "right",
                labels: {
                    fontColor: "gray"
                },
                display: true,
            },
            elements: {
                hitRadius: 3,
            }
    }
});

let expenses_vs_category_chart = new Chart(document.getElementById("expenses_vs_category"), {
    type: 'bar',
    data: {
        labels: category_expenses_labels,
        datasets: [{
            label: "Categories Of Expenses",
            data: category_expenses_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#60BD68',
                '#E16851','#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                min: getAxisMinimum(category_expenses_values),
            }
        },
        title: {
            display: true,
            text: "Expenses per Categories in selected month",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

let expense_pie_chart = new Chart(document.getElementById("expense_pie"), {
    type: 'pie',
    data: {
        labels: category_expenses_labels,
        datasets: [{
            label: "Expenses",
            data: category_expenses_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#60BD68',
                '#E16851','#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        title: {
            display: true,
            text: "Expenses per Categories in selected month",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

let incomes_year_vs_category_chart = new Chart(document.getElementById("incomes_year_vs_category"), {
    type: 'bar',
    data: {
        labels: category_incomes_year_labels,
        datasets: [{
            label: "Categories Of Incomes",
            data: category_incomes_year_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#E16851', '#60BD68',
                '#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                min: getAxisMinimum(category_incomes_year_values),
            }
        },
        title: {
            display: true,
            text: "Incomes per Categories in selected year",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

let income_year_pie_chart = new Chart(document.getElementById("income_year_pie"), {
    type: 'pie',
    data: {
        labels: category_incomes_year_labels,
        datasets: [{
            label: "Expenses",
            data: category_incomes_year_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#E16851', '#60BD68',
                '#FF66B2', '#FB8267', '#B276B2'],

            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        title: {
            display: true,
            text: "Incomes per Categories in the selected year",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

let incomes_vs_category_chart = new Chart(document.getElementById("incomes_vs_category"), {
    type: 'bar',
    data: {
        labels: category_incomes_labels,
        datasets: [{
            label: "Categories Of Incomes",
            data: category_incomes_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#E16851', '#60BD68',
                        '#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        scales: {
            y: {
                beginAtZero: false,
                min: getAxisMinimum(category_incomes_values),
            }
        },
        title: {
            display: true,
            text: "Incomes per Categories in the selected month",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});

let income_pie_chart = new Chart(document.getElementById("income_pie"), {
    type: 'pie',
    data: {
        labels: category_incomes_labels,
        datasets: [{
            label: "Expenses",
            data: category_incomes_values,
            backgroundColor: ['#5DA5DA ', '#FAA43A', '#E16851', '#60BD68',
                '#FF66B2', '#FB8267', '#B276B2'],
            borderWidth: 1,
            hoverBorderColor: "black",
            hoverBorderWidth: 2,
            hoverBackgroundColor: 'rgba(135, 177, 215)',
            pointHoverRadius: 5
        }],
    },
    options: {
        title: {
            display: true,
            text: "Incomes per Categories in the selected month",
            fontSize: 20,
        },
        legend: {
            position: "right",
            labels: {
                fontColor: "gray"
            },
            display: true,
        },
        elements: {
            hitRadius: 3,
        }
    }
});