$(document).ready(function(){
    $('.button-collapse').sideNav();
    $('.parallax').parallax();
    $('.select').material_select();
    $('.datepicker').pickadate({
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 15, // Creates a dropdown of 15 years to control year
        format: 'dd-mm-yyyy'});
});
