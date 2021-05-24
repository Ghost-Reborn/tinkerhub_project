let pswd_fields = {'login-pswd': [false, 'login-switch-pswd'],
                    'sign_up-pswd-1': [false, 'sign_up-switch-pswd-1'],
                    'sign_up-pswd-2': [false, 'sign_up-switch-pswd-2'],
                    'update-pswd-1': [false, 'update-switch-pswd-1'],
                    'update-pswd-2': [false, 'update-switch-pswd-2'],
                    'update-pswd-3': [false, 'update-switch-pswd-3']};

let menu=false;

function showPassword(pswd_field_name)
{
    show_pswd = pswd_fields[pswd_field_name][0];
    crnt_pswd_field = document.getElementById(pswd_field_name);
    crnt_pswd_status = document.getElementById(pswd_fields[pswd_field_name][1]);
    if(show_pswd != true)
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

function fnShowMenu()
{
	if(menu==false)
	{
		document.getElementById('hamburger').innerHTML = 'Close';
		document.getElementById('menu_container').style.display = 'block';
		menu=true;
	}
	else
	{
		
		document.getElementById('hamburger').innerHTML = 'Menu';
		document.getElementById('menu_container').style.display = 'none';
		menu=false;
	}
	
}