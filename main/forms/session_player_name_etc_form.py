'''
 staff page, edit name etc form
'''

from django import forms

class StaffEditNameEtcForm(forms.Form):
    '''
    staff page, edit name etc form
    '''
    def __init__(self, *args, **kwargs):
        prolific_mode = kwargs.pop('prolific_mode', None)
        super(StaffEditNameEtcForm, self).__init__(*args, **kwargs)

        if prolific_mode:
            self.fields['name'].label = "Prolific Session ID"
            self.fields['student_id'].label = "Prolific Subject ID"
            del self.fields['email']
        
    name = forms.CharField(label='Full Name',
                           required=False,
                           widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.name",
                                                         "autocomplete":"off",
                                                         "v-on:keyup.enter":"sendUpdateSubject()"}))

    student_id = forms.CharField(label='Student ID',
                                 required=False,
                                 widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.student_id",
                                                               "v-on:keyup.enter":"sendUpdateSubject()"}))

    email =  forms.EmailField(label='Email',
                              required=False,
                              widget=forms.EmailInput(attrs={"v-model":"staffEditNameEtcForm.email",
                                                             "v-on:keyup.enter":"sendUpdateSubject()"}))
    

