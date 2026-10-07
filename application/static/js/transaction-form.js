"use strict";

const categoryTree = JSON.parse(
    document.getElementById("category-data").textContent
);

const typeField = document.getElementById("transactionType");
const categoryField = document.getElementById("firstCategory");
const subcategoryField = document.getElementById("secondCategory");

function setOptions(field, values, selectedValue = "") {
    field.replaceChildren(new Option("Select...", ""));

    for (const value of values) {
        field.add(new Option(value, value));
    }

    field.value = values.includes(selectedValue)
        ? selectedValue
        : "";
}

function updateSubcategories(selectedValue = "") {
    const categories = categoryTree[typeField.value] || {};
    const subcategories = categories[categoryField.value] || [];

    setOptions(subcategoryField, subcategories, selectedValue);
}

function updateCategories(
    selectedCategory = "",
    selectedSubcategory = ""
) {
    const categories = categoryTree[typeField.value] || {};

    setOptions(
        categoryField,
        Object.keys(categories),
        selectedCategory
    );

    updateSubcategories(selectedSubcategory);
}

typeField.addEventListener("change", () => {
    updateCategories();
});

categoryField.addEventListener("change", () => {
    updateSubcategories();
});

// Preserve valid selections when the form is displayed again.
updateCategories(
    categoryField.value,
    subcategoryField.value
);