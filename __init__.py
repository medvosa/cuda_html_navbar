import os
from cudatext import *
import re

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_html_navbar.ini')


class Command:
    def add_button(self,text):
        toolbar_proc(self.form_to_toolbar[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]], TOOLBAR_ADD_ITEM)
        count = self.count_buttons
        self.count_buttons+=1
        print(self.form_to_toolbar[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]])
        if not ed.get_prop(PROP_TAB_ID) in self.buttons:
            self.buttons[ed.get_prop(PROP_TAB_ID)]=[]
        btn_id = toolbar_proc(self.form_to_toolbar[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]], TOOLBAR_GET_BUTTON_HANDLE, index=count-1)
        if btn_id:
            self.buttons[ed.get_prop(PROP_TAB_ID)].append(btn_id)
        def callbackf():
            try:
                self.need_action=False
                coord=self.cors[count-1-self.buttons_hidden[ed.get_prop(PROP_TAB_ID)]]
                line=ed.get_text_line(coord[0])
                new_x=coord[1]
                while new_x>0:
                    if line[new_x]=='<':
                        break
                    new_x-=1
                new_x+=1
                ed.set_caret(new_x,coord[0])
            finally:
                pass
        if btn_id:
            button_proc(btn_id,BTN_SET_KIND,BTNKIND_TEXT_ONLY)
            button_proc(btn_id, BTN_SET_DATA1, callbackf)
    
    def set_buttons(self,buttons):
        print('setting buttons \n'+
           'form_to_tb      : '+str(self.form_to_toolbar)+'\n'+
           ''+
           'all tb_id       : '+str(self.tb_id)+'\n'+
           'tab id          : '+str(ed.get_prop(PROP_TAB_ID))+'\n'+
           'tab to form     : '+str(self.tab_to_form)+'\n'+
           'form to toolbar : '+str(self.form_to_toolbar))
        if not (self.tab_to_form[ed.get_prop(PROP_TAB_ID)] in self.form_to_toolbar):
            tb_i = dlg_proc(self.tab_to_form[ed.get_prop(PROP_TAB_ID)], DLG_CTL_ADD, 'toolbar')
            self.tb_id.append(dlg_proc(self.tab_to_form[ed.get_prop(PROP_TAB_ID)], DLG_CTL_HANDLE, index=toolbar))
            self.form_to_toolbar[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]]=self.tb_i[-1]
            dlg_proc(self.form[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]], DLG_CTL_PROP_SET, index=toolbar, prop={
              'name': 'tb'+str(self.form[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]]),
              'x': 0,
              'y': 0,
              'w': 20,
              'h': 40,
              'align': ALIGN_TOP,
              #'color': 0x80B080,
            }) 
        print('tb_id           : '+str(self.form_to_toolbar[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]])+'\n')
        j=0
        if not ed.get_prop(PROP_TAB_ID) in self.buttons:
            self.buttons[ed.get_prop(PROP_TAB_ID)]=[]
        for i in self.buttons[ed.get_prop(PROP_TAB_ID)]:
            if j>len(buttons):
                button_proc(i,BTN_SET_VISIBLE,False)
                self.buttons_hidden[ed.get_prop(PROP_TAB_ID)]+=1
            j+=1
        j=0
        index=0
        
        for i in buttons:
            if j>=len(self.buttons[ed.get_prop(PROP_TAB_ID)]):
                self.add_button(i)
            else:
                button_proc(self.buttons[ed.get_prop(PROP_TAB_ID)][j],BTN_SET_VISIBLE,True)
                def callbackf(tindex=index):
                    try:
                        self.need_action=False
                        coord=self.cors[tindex]
                        line=ed.get_text_line(coord[0])
                        new_x=coord[1]
                        while new_x>0:
                            if line[new_x]=='<':
                                break
                            new_x-=1
                        new_x+=1
                        ed.set_caret(new_x,coord[0])
                    finally:
                        pass
                index+=1
                button_proc(self.buttons[ed.get_prop(PROP_TAB_ID)][j],BTN_SET_DATA1,callbackf)
                button_proc(self.buttons[ed.get_prop(PROP_TAB_ID)][j],BTN_SET_TEXT,buttons[j])
            j+=1
        toolbar_proc(self.form_to_toolbar[self.tab_to_form[ed.get_prop(PROP_TAB_ID)]], TOOLBAR_UPDATE)
    
    def parse_html(self,text):
        ignore_list=['meta','br','hr','link']
        strs=[]
        snum=0
        arrs=text.split('<!--')
        text2=''
        ind=0
        closed = True
        for i in arrs:
            closed=False
            if ind==0:
                closed=True
            text2+=' '*4
            if '-->' in i :
                for j in i.split('-->')[0]:
                    if j =='\n':
                        text2+='\n'
                    else:
                        text2+=' '
                for j in i.split('-->')[1]:
                    text2+=j
                closed = True
            elif (ind==0) or closed:
                for j in i:
                    text2+=j
            elif ind==len(arrs)-1:
                for j in i.split('-->')[0]:
                    if j =='\n':
                        text2+='\n'
                    else:
                        text2+=' '
            else:
                text2+=' '*3      
                if len(i.split('-->'))>1:
                    text2+=i.split('-->')[1]
            ind+=1
        for s in text2.split('\n'):
            flag=0
            cs=''
            colnum=0
            for i in s:
                if i=='<':
                    flag=1
                elif i=='>':
                    flag=0
                    cs=cs.split(' ')[0]
                    if not cs in ignore_list and len(cs)>0:
                        if not cs[0]=='!':
                            strs.append(cs)
                            self.cors.append([snum,colnum])
                    cs=''
                elif flag==1:
                    cs+=i
                colnum+=1
            i=0
            while i<len(strs):
                if strs[i][0]=='/':
                    tag=strs[i][1:]
                    j=i
                    while j>=0:
                        j-=1
                        if strs[j]==tag:
                            break
                    if j>=0:
                        while j<=i:
                            i-=1
                            strs.pop(j)
                            self.cors.pop(j)
                i+=1
            i=0
            while i<len(strs):
                if strs[i]=='script':
                    j=i+1
                    while j<len(strs):
                        strs.pop(j)
                        self.cors.pop(j)
                        j+=1
                i+=1
            self.set_buttons(strs)
            self.strs=strs
            snum+=1
    
    def get_color(self):
        theme=app_proc(PROC_THEME_UI_DATA_GET,'')
        bg_color=0
        for i in theme:
            if i['name']=='EdTextBg':
                bg_color=i['color']
                break
        if not bg_color:
            bg_color=333333
        return bg_color
    
    def __init__(self):
        self.option_lexers=ini_read(fn_config, 'op', 'lexers', 'HTML.*|XML')
        self.buttons_hidden={ed.get_prop(PROP_TAB_ID):0}
        self.count_buttons=0
        self.buttons={}
        self.buttons[ed.get_prop(PROP_TAB_ID)]=[]
        self.cors=[]
        self.form=[dlg_proc(0,DLG_CREATE)]   
        self.tab_to_form={}
        self.tab_to_form[ed.get_prop(PROP_TAB_ID)]=self.form[0]
        self.need_action=True
        self.form_to_toolbar={}
        bg_color=self.get_color()
        dlg_proc(self.form[0], DLG_PROP_SET, prop={                       
          'h':0,
          'visible':False,
          'color':bg_color,
        })                                              
        toolbar = dlg_proc(self.form[0], DLG_CTL_ADD, 'toolbar')
        self.form_to_toolbar[self.form[0]]=dlg_proc(self.form[0], DLG_CTL_HANDLE, index=toolbar)
        toolbar_proc(toolbar,TOOLBAR_THEME)
        dlg_proc(self.form[0], DLG_CTL_PROP_SET, index=toolbar, prop={
          'name': 'tb',
          'x': 0,
          'y': 0,
          'w': 20,
          'h': 40,
          'align': ALIGN_TOP,
          #'color': 0x80B080,
        }) 
        
        self.tb_id = [dlg_proc(self.form[0], DLG_CTL_HANDLE, index=toolbar)]
        self.set_buttons([])
        dlg_proc(self.form[0],DLG_DOCK, index=ed.get_prop(PROP_HANDLE_PARENT), prop='T')                                 
        dlg_proc(self.form[0],DLG_SHOW_NONMODAL)
        #dlg_proc(self.form,TREE_THEME)
        toolbar_proc(toolbar,TOOLBAR_THEME)                   
        pass 
        
    def config(self):
        ini_write(fn_config, 'op', 'lexers', self.option_lexers)
        file_open(fn_config)
    
    def on_open(self, name):
        lexer=ed.get_prop(PROP_LEXER_FILE,'')
        if not lexer:return
        correct_lexer=False
        pattern=re.compile(self.option_lexers)   
        if pattern.fullmatch(lexer):
               correct_lexer=True
        if correct_lexer:
            dlg_proc(self.form[0], DLG_PROP_SET, prop={                       
                'h':25,
                'visible':True,
              })
        else:
            dlg_proc(self.form[0], DLG_PROP_SET, prop={                       
              'h':0,
              'visible':True,
            })
                    
    def on_lexer(self,ed_self):
        self.on_open('')
        pass
        
    
    def on_tab_change(self,ed_self):
        self.on_lexer(ed_self)
                                
        
        if ed_self.get_prop(PROP_TAB_ID) in self.tab_to_form:
            print('exists')
            #print('toolbar id: '+str(self.form_to_toolbar[self.tab_to_form[ed_self.get_prop(PROP_TAB_ID)]]))
        else:
            lexer=ed.get_prop(PROP_LEXER_FILE,'')
            ##
            if not lexer:return
            correct_lexer=False
            pattern=re.compile(self.option_lexers)
            print('checking')   
            if pattern.fullmatch(lexer):
                   correct_lexer=True
            if correct_lexer:
                self.form.append(dlg_proc(0,DLG_CREATE))
                form_i=len(self.form)-1
                                                               
                self.tab_to_form[ed_self.get_prop(PROP_TAB_ID)]=self.form[form_i] 
                dlg_proc(self.form[form_i], DLG_PROP_SET, prop={                       
                    'h':25,
                    'visible':True,
                })
                
                print(len(self.form))
                toolbar=dlg_proc(self.form[form_i], DLG_CTL_ADD, 'toolbar')
                dlg_proc(self.form[form_i], DLG_CTL_HANDLE, index=toolbar)
                print('toooooobar '+str(toolbar))
                self.tb_id.append(dlg_proc(self.form[form_i], DLG_CTL_HANDLE, index=toolbar))
                toolbar_proc(toolbar,TOOLBAR_THEME)
                dlg_proc(self.form[form_i], DLG_CTL_PROP_SET, index=toolbar, prop={
                   'name': 'tb'+str(form_i),
                   'x': 0,
                   'y': 0,
                   'w': 20,
                   'h': 40,
                   'align': ALIGN_TOP,
                   #'color': 0x80B080,
                }) 
                print('created toolbar '+str(toolbar))
                self.form_to_toolbar[self.form[form_i]]=dlg_proc(self.form[form_i], DLG_CTL_HANDLE, index=toolbar)
                print(len(self.form_to_toolbar))
                toolbar_proc(toolbar,TOOLBAR_UPDATE)
                dlg_proc(self.form[form_i],DLG_DOCK, index=ed.get_prop(PROP_HANDLE_PARENT), prop='T')               
                dlg_proc(self.form[form_i],DLG_SHOW_NONMODAL)        
                print('creating')
                print(self.tab_to_form)
                print(self.form_to_toolbar)
                print(self.tb_id)
            print('does not exist') 
        self.on_caret(ed_self)
    
    def on_caret(self, ed_self):
        if self.need_action:
            if ed_self.get_prop(PROP_TAB_ID) in self.tab_to_form:
                self.cors=[]
                x1,y1,x2,y2=ed_self.get_carets()[0]
                self.parse_html(ed_self.get_text_substr(0,0,x1,y1))
        self.need_action=True
