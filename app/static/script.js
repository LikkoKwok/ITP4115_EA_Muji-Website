function showForm(formType) {
    const personalForm = document.getElementById('personal-form');
    const organizationForm = document.getElementById('organization-form');
    
    if(formType === 'personal') {
        personalForm.style.display = 'block';
        organizationForm.style.display = 'none';
    } else {
        personalForm.style.display = 'none';
        organizationForm.style.display = 'block';
    }
}
function initFormSwitch() {
    const path = window.location.pathname;
    document.querySelectorAll('.form-switch button').forEach(btn => {
        btn.parentElement.style.backgroundColor = 
            path.includes(btn.dataset.formType) ? '#eee' : 'transparent';
    });
}
window.onload = initFormSwitch;
