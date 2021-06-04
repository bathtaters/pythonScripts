# Parse Premiere EDL for audio filenames
# NOTE: Video/Transitions don't work
# NOTE: Type 'main()' to output csv


filename = '/path/to/EDL.edl'
outfile = '/path/to/output.csv'
TABLE_STYLE = 3 # 1-3
# TABLE_STYLES:
# 1) EDL: {name}; Clip Name, Clip TC In, Clip TC Out;
# 2) {name[:14]}; Timeline In, Clip Name, Clip TC In, Clip TC Out;
# 3) {name}; Timeline In, Clip Name, Clip TC In, Clip TC Out, Clip Length;


        



class Timecode:

    film_type = '16mm'
    timebase = 24
    playspeed = 1.0
    
    LIMITS = [100,60,60,100]
    FOOTCOUNT = { '16mm' : 20,
                  '35mm' : 16 }
              

    def __init__(self,tc):
        if type(tc) is tuple: tc = list(tc)
        self.negative = False

        if type(tc) is Timecode:
            self.negative = tc.negative
            self.init_list(tc.tcarray)
        elif type(tc) is int: self.init_int(tc)
        elif type(tc) is str: self.init_str(tc)
        elif type(tc) is list: self.init_list(tc)
        else: self.init_err()
            
    def init_str(self, tc):
        tc = tc.strip().replace(',','')
        if tc.strip()[0] == '-':
            self.negative = not(self.negative)
            tc = tc[1:]
            
        if tc.isdigit(): self.init_int(int(tc))
        elif ':' in tc: self.init_list(Timecode.intlist(tc.split(':')))
        elif '+' in tc: self.init_int(Timecode.ff_to_frames(*Timecode.intlist(tc.split('+'))))
        else: self.init_err()

    def init_err(self):
        print('Error with TC [',tc,']. Set to 0.')
        self.init_int(0)

    def init_int(self,tc):
        if tc < 0:
            self.negative = not(self.negative)
            tc = -tc
        self.init_list([0,0,0,tc])
        
    def init_list(self, tc):
        if tc[0] < 0:
            self.negative = not(self.negative)
            tc[0] = -tc[0]
        self.set_tc(tc)
        
                       
    def set_tc(self,tc):
        for i in range(max(4-len(tc),0)):
            tc.insert(0,0)
        tc = tc[:4]
        tc = Timecode.fix_tc_array(tc)
        
        self.tcarray = tc

        return tc

    
    
    def intlist(array):
        int_arr = []
        for entry in array:
            if entry.isdigit(): int_arr.append(int(entry))
            else: print('"'+str(entry)+'" omitted from TC array:',array)
        return int_arr

    def fix_tc_array(tc):
        tc = list(tc)
        for i in range(3,-1,-1):
            limit = Timecode.LIMITS[i]
            if i == 3: limit = Timecode.timebase
            tc[i-1] = tc[i-1] + (tc[i] // limit)
            tc[i] = tc[i] % limit
        return tc
        
    def ff_to_frames(feet, frames):
        return (feet * Timecode.FOOTCOUNT.get(Timecode.film_type)) + frames

    def hh(self):
        return self.tcarray[0]

    def mm(self):
        return self.tcarray[1]

    def ss(self):
        return self.tcarray[2]

    def ff(self):
        return self.tcarray[3]

    def framecount(self):
        fc = (self.hh()*Timecode.LIMITS[1] + self.mm())*Timecode.LIMITS[2]
        fc = (fc + self.ss())*Timecode.timebase + self.ff()
        return (self.negative * -2 + 1) * fc
    
    def framerate(self=None):
        return Timecode.timebase * Timecode.playspeed

    def sign(self):
        sign = '+'
        if self.negative: sign = '-'
        return sign

    def __str__(self):
        txt = self.sign().replace('+','')
        for x in self.tcarray:
            txt = txt + str(x).zfill(2) + ':'
        return txt[:-1]

    def __repr__(self):
        SGN = { '+' : '(Positive)', '-' : '(Negative)' }
        txt = self.sign() + '[' + str(self) + ']\n'
        txt = txt + SGN[self.sign()] +' Hours: '+str(self.hh())
        txt = txt + '; Minutes: '+str(self.mm())+'; Seconds: '+str(self.ss())
        txt = txt + '; Frames: '+str(self.ff())+'\n'
        txt = txt + '[Object Variables]\n'
        txt = txt + 'film_type: ' + Timecode.film_type
        txt = txt + '; timebase: ' + str(Timecode.timebase)
        txt = txt + '; playspeed: ' + str(Timecode.playspeed)
        txt = txt + '; framerate: ' + str(Timecode.framerate())
        return txt
         

    def __bool__(self):
        for x in self.tcarray:
            if x != 0: return True
        return False

    def __lt__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return self.framecount() < x

    def __le__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return self.framecount() <= x

    def __eq__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return self.framecount() == x

    def __ne__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return self.framecount() != x

    def __gt__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return self.framecount() > x

    def __ge__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return self.framecount() >= x

    def __add__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return Timecode(self.framecount() + x)

    def __sub__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return Timecode(self.framecount() - x)

    def __mul__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return Timecode(self.framecount() * x)

    def __truediv__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return Timecode(self.framecount() / x)

    def __floordiv__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return Timecode(self.framecount() // x)

    def __mod__(self, other):
        x = other
        if type(other) is Timecode: x = other.framecount()
        return Timecode(self.framecount() % x)

    def __neg__(self):
        new = Timecode(self)
        new.negative = not(self.negative)
        return new

    def __pos__(self):
        new = Timecode(self)
        new.negative = self.negative
        return new

    def __invert__(self):
        new = Timecode(self)
        new.negative = not(self.negative)
        return new

    def __abs__(self):
        new = Timecode(self)
        new.negative = False
        return new


class Edit:

    NAME_DEF = '[No Name Found]'
    MEDIA = {'AA' : 'Audio', 'V' : 'Video', 'NONE' : 'None'}
    DEFS = ( (0, 'edit_num', 8),
             (1, 'reel', 9),
             (2, 'media', 5),
             (3, 'c', 2),
             (4, 'b', 7),
             (5, 'clip_in', 12),
             (6, 'clip_out', 12),
             (7, 'edit_in', 12),
             (8, 'edit_out', 12) )
    INT_DEFS = (0,)
    TC_DEFS = (5,6,7,8)
    

    def __init__(self,line,name=''):

        if name in ('',None,False,0): name = Edit.NAME_DEF
        self.name = name
        self.is_edit = True
        p = 0
        for d in Edit.DEFS:
            if p > len(line): break
            data = line[p:p+d[2]].strip()
            if d[0] in Edit.INT_DEFS:
                if data.isdigit(): data = int(data)
                #elif data == '': data = 0
                else:
                    self.is_edit = False
                    break
            elif d[0] in Edit.TC_DEFS: data = Timecode(data)
            if d[1] == 'media': data = Edit.MEDIA.get(data,data)
            self.__dict__[d[1]] = data
            p = p + d[2]

    def set_name(self,name):
        self.name = name
        return self.name

    def mmatch(self, mtype):
        if mtype == '': return True
        if type(mtype) not in (list,tuple): mtype = (mtype,)
        return self.media in mtype

    def same(self, other):
        if not(self.is_edit) and not(other.is_edit): return True
        elif not(self.is_edit) or not(other.is_edit): return False
        # Use MORE IN DEPTH TEST
        return self.edit_num == other.edit_num

    def is_named(self):
        return self.name != Edit.NAME_DEF

    def __repr__(self):
        rep = '--EDIT--\nname: ' + self.name + '\nis_edit: '+str(self.is_edit)+'\n'
        for d in Edit.DEFS:
            rep = rep + d[1] + ': ' + str(self.__dict__.get(d[1],'N/A')) + '\n'
        return rep
        
    def __str__(self):
        return str(self.edit_num).zfill(6)+' '+self.name+' '+str(self.clip_in)

    def __bool__(self):
        return self.is_edit and (self.edit_num not in (0,None,''))

    def __int__(self):
        if type(self.edit_num) is not int: return -1
        return int(self.edit_num)

    def __index__(self):
        return self.__int__()
    
    def __lt__(self, other):
        if type(other) is int: return self.edit_num < other
        elif type(other) is Edit: return self.clip_in < other.clip_in
        raise NotImplemented

    def __le__(self, other):
        if type(other) is int: return self.edit_num <= other
        elif type(other) is Edit: return self.clip_in <= other.clip_in
        raise NotImplemented

    def __eq__(self, other):
        if type(other) is int: return self.edit_num == other
        elif type(other) is Edit: return self.clip_in == other.clip_in
        raise NotImplemented

    def __ne__(self, other):
        if type(other) is int: return self.edit_num != other
        elif type(other) is Edit: return self.clip_in != other.clip_in
        raise NotImplemented

    def __gt__(self, other):
        if type(other) is int: return self.edit_num > other
        elif type(other) is Edit: return self.clip_in > other.clip_in
        raise NotImplemented

    def __ge__(self, other):
        if type(other) is int: return self.edit_num >= other
        elif type(other) is Edit: return self.clip_in >= other.clip_in
        raise NotImplemented
    
        

class Edl:

    EDLNAME = 'TITLE: '
    CLIPNAME = { '* FROM CLIP NAME: ' : 'Audio',
                 '* KEY CLIP NAME: ' : 'Video',
                 '* FROM CLIP NAME: ' : 'None' } 

    def __init__(self, file, media_type=''):
        self.filename = file
        self.name = Edl.get_title(file)
        self.edits = Edl.get_edits(file,media_type)
    
    def get_title(file):
        with open(file,'r') as f:
            for line in f:
                if line[:len(Edl.EDLNAME)] == Edl.EDLNAME:
                    return line[len(Edl.EDLNAME):].strip()
        return file[file.rfind('/')+1:f.rfind('.')]
                
    
    def get_edits(file, media=''):
        edits = []
        with open(file,'r') as f:
            saved = None
            for line in f:
                new = Edit(line)
                if new:
                    if saved:
                        if saved.same(new): continue # Eliminates same edit numbers
                        edits.append(saved)
                        saved = None
                    if new.mmatch(media): saved = new
                
                elif saved and not saved.is_named():
                    for key in Edl.CLIPNAME.keys():
                        if line[:len(key)] == key:
                            saved.set_name(line[len(key):].strip())
                            break

            if saved: edits.append(saved)

        return edits


    def get_table_a(self,row=',',col='\n'):
        # EDL: {name}; Clip Name, Clip TC In, Clip TC Out;
        txt = 'EDL: '+self.name+col
        txt = txt+'Clip Name'+row+'Clip TC In'+row+'Clip TC Out'+col
        for e in self:
            txt = txt + e.media +row+ str(e.edit_in) +row+ str(e.edit_out) +col
            txt = txt + e.name +row+ str(e.clip_in) +row+ str(e.clip_out) +col+col
        return txt[:-1]

    def get_table_b(self,row=',',col='\n'):
        # {name[:14]}; Timeline In, Clip Name, Clip TC In, Clip TC Out;
        txt = self.name[:14]+col
        txt = txt+'Timeline In'+row+'Clip Name'+row+'Clip TC In'+row+'Clip TC Out'+col
        for e in self:
            txt = txt + str(e.edit_in) +row+ e.name +row+ str(e.clip_in) +row+ str(e.clip_out) +col
        return txt[:-1]

    def get_table_c(self,row=',',col='\n'):
        # {name}; Timeline In, Clip Name, Clip TC In, Clip TC Out, Clip Length;
        txt = self.name+col
        txt = txt+'Timeline In'+row+'Clip Name'+row+'Clip TC In'+row+'Clip TC Out'+row+'Clip Length'+col
        for e in self:
            txt = txt + str(e.edit_in) +row+ e.name +row+ str(e.clip_in) +row+ str(e.clip_out) +row+ str(e.clip_out-e.clip_in) +col
        return txt[:-1]

    def get_table(self, choice=1, row=',', col='\n'):
        table_method = { 1 : self.get_table_a,
                         2 : self.get_table_b,
                         3 : self.get_table_c }
        if choice not in table_method.keys(): choice = 1
        return table_method[choice](row,col)

    def __repr__(self):
        txt = '------EDL------\nName: '+self.name+'\n\n'
        for e in self:
            txt = txt + e.__repr__() + '\n'
        return txt[:-1]
    
    def __str__(self):
        txt = 'EDL: '+self.name+'\n'
        for e in self:
            txt = txt + str(e) + '\n'
        return txt[:-1]
    
    def __len__(self):
        return len(self.edits)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        self.index = self.index + 1
        if self.index > len(self): raise StopIteration
        return self.edits[self.index - 1]

    def __getitem__(self, index):
        return self.edits[index]


    


def main():
    inp = Edl(filename,'Audio')
    with open(outfile,'w') as of:
        of.write(inp.get_table(TABLE_STYLE))
    return 0
