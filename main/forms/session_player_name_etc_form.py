'''
 staff page, edit name etc form
'''

from django import forms

class StaffEditNameEtcForm(forms.Form):
    '''
    staff page, edit name etc form
    '''
    name = forms.CharField(label='Full Name',
                           required=False,
                           widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.name",
                                                         "v-on:keyup.enter":"sendUpdateSubject()"}))

    student_id = forms.CharField(label='Student ID',
                                 required=False,
                                 widget=forms.TextInput(attrs={"v-model":"staffEditNameEtcForm.student_id",
                                                               "v-on:keyup.enter":"sendUpdateSubject()"}))

    email =  forms.EmailField(label='Email',
                              required=False,
                              widget=forms.EmailInput(attrs={"v-model":"staffEditNameEtcForm.email",
                                                             "v-on:keyup.enter":"sendUpdateSubject()"}))
