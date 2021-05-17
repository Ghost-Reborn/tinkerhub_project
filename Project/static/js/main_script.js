let pswd_fields = {'login-pswd': [false, 'login-switch-pswd']};

function showPassword(pswd_field_name)
{
    show_pswd = pswd_fields[pswd_field_name][0];
    crnt_pswd_field = document.getElementById(pswd_field_name);
    crnt_pswd_status = document.getElementById(pswd_fields[pswd_field_name][1]);
    if(show_pswd == true)
    {
        crnt_pswd_field.setAttribute('type', 'text');
        crnt_pswd_status.innerHTML = "Hide Password";
    }
    else
    {
        crnt_pswd_field.setAttribute('type', 'password');
        crnt_pswd_status.innerHTML = "Show Password";
    }
    pswd_fields[pswd_field_name][0] = !show_pswd;
}