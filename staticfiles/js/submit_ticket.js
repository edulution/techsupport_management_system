const handleSubcategoryUpdate = () => {
  const categoryId = document.getElementById('id_category').value;
  fetch(`/get_subcategories/?category_id=${categoryId}`)
    .then(response => response.json())
    .then(data => {
      const subcategoriesDropdown = document.getElementById('id_subcategory');
      subcategoriesDropdown.innerHTML = '';

      data.subcategories.forEach(subcategory => {
        const option = document.createElement('option');
        option.value = subcategory.id;
        option.text = subcategory.name;
        subcategoriesDropdown.appendChild(option);
      });
    })
    .catch(error => {
      console.error('Error fetching subcategories:', error);
    });
};

// Trigger subcategory update on page load and category change
document.addEventListener('DOMContentLoaded', handleSubcategoryUpdate);
document.getElementById('id_category').addEventListener('change', handleSubcategoryUpdate);