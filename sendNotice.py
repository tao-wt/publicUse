#!/usr/bin/envspacepythonPLY#spaceencoding:utf-8PLY__author__space=space'sainter'PLYPLYimportspacesysPLY#fromspacelib.ParamikoClassspaceimportspace*PLY#fromspacelib.PublicSQLClassspaceimportspace*PLYimportspacesubprocessPLYimportspacemultiprocessingPLYimportspacesqlite3PLYfromspaceoptparsespaceimportspaceOptionParserPLYimportspacerePLYPLYclassspaceSqliteClass(object):PLYPLYTABdefspace__init__(self,dbname):PLYTABTABself.dbnamespace=spacedbnamePLYTABTABself.connspace=spacesqlite3.connect(self.dbname)PLYTABTABself.curspace=spaceself.conn.cursor()PLYPLYTABdefspacequery(self,sql):PLYTABTABtry:PLYTABTABTABn=self.cur.execute(sql)PLYTABTABTABreturnspacenPLYTABTABexceptspacesqlite3.Error,e:PLYTABTABTABprintspace"sqlitespaceError:%s\nSQL:%s"space%(e,sql)PLYPLYTABdefspacequeryAll(self,sql):PLYTABTABself.query(sql)PLYTABTABresultspace=spaceself.cur.fetchall()PLYTABTABnew_listspace=[]PLYTABTABforspaceinvspaceinspaceresult:PLYTABTABTABdspace=space[]PLYTABTABTABforspaceispaceinspacerange(0,len(inv)):PLYTABTABTABTABd.append(inv[i])PLYTABTABTABnew_list.append(d)PLYTABTABreturnspacenew_listPLYPLYTABdefspacecommit(self):PLYTABTABself.conn.commit()PLYPLYTABdefspaceclose(self):PLYTABTABself.cur.close()PLYTABTABself.conn.close()PLYPLYclassspaceSQLClass(object):PLYTABsspace=spaceSqliteClass('/home/nagios/modError.db')PLYPLYTABdefspacecheckInfo(self,ip,mod):PLYTABTABsql='selectspace*spacefromspacemodErrorspacewherespaceip="%s"spaceandspacemod="%s";'%(ip,mod)PLYTABTABreturnspaceself.s.queryAll(sql)PLYTABTABPLYTABdefspaceinsInfo(self,ip,mod):PLYTABTABsqlspace=space'insertspaceintospacemodErrorspace(ip,mod)spacevalues("%s","%s");'%(ip,mod)PLYTABTAB#printspacesqlPLYTABTABself.s.queryAll(sql)PLYTABTABself.s.commit()PLYPLYTABdefspacedelInfo(self,ip,mod):PLYTABTABsqlspace=space"deletespacefromspacemodErrorspacewherespaceip='%s'spaceandspacemod='%s';"space%(ip,mod)PLYTABTAB#printspacesqlPLYTABTABself.s.queryAll(sql)PLYTABTABself.s.commit()PLYPLYparserspace=spaceOptionParser(add_help_option=0)PLY#spaceparser.add_option("-h",space"--help",spaceaction="callback",spacecallback=helpFunc)PLY#spaceparser.add_option("-v",space"-V",space"--version",spaceaction="callback",spacecallback=verFunc)PLYparser.add_option("-S",space"--stat",spaceaction="store",spacetype="string",spacedest="stat",default="")PLYparser.add_option("-M",space"--module",spaceaction="store",spacetype="string",spacedest="mod",default="")PLYparser.add_option("-i",space"--ip",spaceaction="store",spacetype="string",spacedest="ip",default="")PLY(options,spaceargs)space=spaceparser.parse_args()PLYmod=options.modPLYip=options.ipPLYstat=options.statPLYcommandoption=argsPLY#printspacestat,ip,modPLYPLYtspace=spaceSQLClass()PLYPLY#checkBspace=spacestat.find("OK")PLYifspacestat.find("RECOVERY")==-1:PLYTABcheckAspace=spacet.checkInfo(ip,mod)PLYTABifspacecheckAspace==space[]:PLYTABTAB#printspace'---'PLYTABTABt.insInfo(ip,mod)PLYelse:PLYTABcheckAspace=spacet.checkInfo(ip,mod)PLYTAB#printspace'+++',checkAPLYTABifspacecheckAspace!=space[]:PLYTABTABt.delInfo(ip,mod)PLYPLY
