node('hzlinb130.china.nsn-net.net'){
    catchError {
    stage("get version"){
        checkout([$class: 'SubversionSCM', additionalCredentials: [], excludedCommitMessages: '', excludedRegions: '',
        excludedRevprop: '', excludedUsers: '', filterChangelog: false, ignoreDirPropChanges: false, includedRegions: '',
        locations: [[credentialsId: 'd0401375-4c27-45f4-bd34-d1aec06cd524', depthOption: 'infinity', ignoreExternalsOption: true,
        local: '.', remote: 'https://beisop60.china.nsn-net.net/isource/svnroot/BTS_D_MZ_CBTS/MZ_releasenote/CBTS18_MZ_0700']], workspaceUpdater: [$class: 'UpdateUpdater']])
        
        sh '''
        if [ -d HZ_CBTS_SCM ];then
            cd ${WORKSPACE}/HZ_CBTS_SCM
            git reset --hard
            git pull
            cd ${WORKSPACE}/
        else
            git clone https://gerrite1.ext.net.nokia.com:443/HZ_CBTS_SCM
        fi

        cat ${WORKSPACE}/*.xml |egrep "<name>"|awk -F "</" '{print $1}'|awk -F ">" '{print $2}' > mz_version.txt
        SVN_REVISION=`svn info https://beisop60.china.nsn-net.net/isource/svnroot/BTS_D_MZ_CBTS/MZ_releasenote/CBTS18_MZ_0700/ |awk '/Last Changed Rev/ {print $NF}'`
        python3 HZ_CBTS_SCM/CiTools/parse_mz_rn.py -r ${WORKSPACE}/MZOAM_releasenote.xml -o mz_modules.txt
        echo "RN_VER=/isource/svnroot/BTS_D_MZ_CBTS/MZ_releasenote/CBTS18_MZ_0700@${SVN_REVISION}" >> mz_modules.txt
        '''

        mz_version = readFile 'mz_version.txt'
        println mz_version
        mystr = readFile 'mz_modules.txt'
        def split=mystr.split("\n")  
        for(item in split){ 
           println item.replaceAll("\"", "")
           if (item.contains("nodeoam")){
               nodeoam=item.replaceAll("\"", "")
           }
           if (item.contains("node-js")){
               nodejs=item.replaceAll("\"", "")
           }
           if (item.contains("env")){
               env_version=item.replaceAll("\"", "")
           }
           if (item.contains("racoam")){
               racoam=item.replaceAll("\"", "")
           }
           if (item.contains("oamagentjs")){
               oamagentjs=item.replaceAll("\"", "")
           }
           if (item.contains("siteoam")){
               siteoam=item.replaceAll("\"", "")
           }
           if (item.contains("alumag")){
               alumag=item.replaceAll("\"", "")
           }
           if (item.contains("pdl-validator")){
               pdlvalidator=item.replaceAll("\"", "")
           }
           if (item.contains("migration-rule")){
               migrationrule=item.replaceAll("\"", "")
           }
           if (item.contains("PS_REL")){
               PS_REL=item.replaceAll("\"", "").split("=")[-1]
           }
           if (item.contains("RCP")){
               RCP=item.replaceAll("\"", "").split("=")[-1]
           }
           if (item.contains("RN_VER")){
               RN_VER=item.replaceAll("\"", "").split("=")[-1]
           }
        }
        
        nodejs_ver=nodejs.split(" ")[-1]
        nodeoam_ver=nodeoam.split(" ")[-1]
        oamagentjs_ver=oamagentjs.split(" ")[-1]
        env_ver=env_version.split(" ")[-1]
        racoam_ver=racoam.split(" ")[-1]
        siteoam_ver=siteoam.split(" ")[-1]
        alumag_ver=alumag.split(" ")[-1]
        pdlvalidator_ver=pdlvalidator.split(" ")[-1]
        migrationrule_ver=migrationrule.split(" ")[-1]
    }
    
    stage("prepare loacl node") {
        node('mz_ci_node') {
            withEnv(["module=nodejs_local",  "module_ver="+nodejs, "force_rebuild="+force_rebuild]) {
                sh '''
                export PATH=~/python2/:${PATH}
                mkdir -p ${WORKSPACE}/${module}
                cd ${WORKSPACE}/${module}
                svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_local_node.sh
                bash mz_ci_local_node.sh -n "${module_ver}" -f "${force_rebuild}"
                '''
            }
        }
    }
    
    stage("parallel build MZ components"){
        buildjobs = [
            oamagentjs_rcp_build : {
                node('mz_ci_node') {
                    withEnv(["module=oamagentjs_rcp", "RCP="+RCP, "module_ver="+oamagentjs, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'rcp' -v "${RCP}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            racoam_rcp_build : {
                node('mz_ci_node') {
                    withEnv(["module=racoam_rcp", "RCP="+RCP, "module_ver="+racoam, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'rcp' -v "${RCP}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            siteoam_rcp_build : {
                node('mz_ci_node') {
                    withEnv(["module=siteoam_rcp", "RCP="+RCP, "module_ver="+siteoam, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'rcp' -v "${RCP}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            nodejs_rcp_build : {
                node('mz_ci_node') {
                    withEnv(["module=nodejs_rcp", "RCP="+RCP, "module_ver="+nodejs, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'rcp' -v "${RCP}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            pdlvalidator_rcp_build : {
                node('mz_ci_node') {
                    withEnv(["module=pdlvalidator_rcp", "RCP="+RCP, "module_ver="+pdlvalidator, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'rcp' -v "${RCP}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            migrationrule_rcp_build : {
                node('mz_ci_node') {
                    withEnv(["module=migrationrule_rcp", "RCP="+RCP, "module_ver="+migrationrule, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'rcp' -v "${RCP}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            
            nodeoam_fsm4_build : {
                node('mz_ci_node') {
                    withEnv(["module=nodeoam_fsm4", "PS_REL="+PS_REL, "module_ver="+nodeoam, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm4' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            oamagentjs_fsm4_build : {
                node('mz_ci_node') {
                    withEnv(["module=oamagentjs_fsm4", "PS_REL="+PS_REL, "module_ver="+oamagentjs, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm4' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            nodejs_fsm4_build : {
                node('mz_ci_node') {
                    withEnv(["module=nodejs_fsm4", "PS_REL="+PS_REL, "module_ver="+nodejs, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm4' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            alumag_fsm4_build : {
                node('mz_ci_node') {
                    withEnv(["module=alumag_fsm4", "PS_REL="+PS_REL, "module_ver="+alumag, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm4' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },

            nodeoam_fsm3_build : {
                node('mz_ci_node') {
                    withEnv(["module=nodeoam_fsm3", "PS_REL="+PS_REL, "module_ver="+nodeoam, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm3' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            oamagentjs_fsm3_build : {
                node('mz_ci_node') {
                    withEnv(["module=oamagentjs_fsm3", "PS_REL="+PS_REL, "module_ver="+oamagentjs, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm3' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            nodejs_fsm3_build : {
                node('mz_ci_node') {
                    withEnv(["module=nodejs_fsm3", "PS_REL="+PS_REL, "module_ver="+nodejs, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm3' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            },
            alumag_fsm3_build : {
                node('mz_ci_node') {
                    withEnv(["module=alumag_fsm3", "PS_REL="+PS_REL, "module_ver="+alumag, "ENV="+env_version, "node_ver="+nodejs_ver, "force_rebuild="+force_rebuild]) {
                        sh '''
                        export PATH=~/python2/:${PATH}
                        mkdir -p ${WORKSPACE}/${module}
                        cd ${WORKSPACE}/${module}
                        svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_build.sh
                        bash mz_ci_build.sh -e "${ENV}" -m "${module_ver}" -p 'fsm3' -v "${PS_REL}" -n "${node_ver}" -f "${force_rebuild}"
                        '''
                    }
                }
            }
        ]
        parallel buildjobs
    }
    
    stage("Deliver"){
        echo "deliver for FSM3 and FSM4"
        println "nodeoam: "+nodeoam_ver
        println "oamagentjs: "+oamagentjs_ver
        println "ENV: "+env_ver
        println "nodejs: "+nodejs_ver
        println "racoam: "+racoam_ver
        println "siteoam: "+siteoam_ver
        println "alumag: "+alumag_ver
        println "pdlvalidator: "+pdlvalidator_ver
        println "migrationrule: "+migrationrule_ver
        println "MZ releasenote: "+RN_VER
        println "PS_REL: "+PS_REL
        println "RCP: "+RCP
        
        
        def r3_commit_version = ''
        def r4_commit_version = ''
        parallel(
            "deliver_r3":{
                checkout([$class: 'SubversionSCM', additionalCredentials: [], excludedCommitMessages: '', excludedRegions: '', excludedRevprop: '',
                excludedUsers: '', filterChangelog: false, ignoreDirPropChanges: false, includedRegions: '',
                locations: [[credentialsId: 'd0401375-4c27-45f4-bd34-d1aec06cd524', depthOption: 'infinity', ignoreExternalsOption: true, local: 'MZ_D_R3',
                remote: 'https://svne1.inside.nsn.com/isource/svnroot/BTS_D_MZ_CBTS/branches/CBTS18_FSM3_MZ_0700']], workspaceUpdater: [$class: 'UpdateWithRevertUpdater']])
                
                withEnv(["RN_VER="+RN_VER, "PS_REL="+PS_REL, "RCP="+RCP, "LTE_MODULE=fsm3", "env="+env_ver, "nodeoam="+nodeoam_ver,
                "nodejs="+nodejs_ver, "racoam="+racoam_ver, "oamagentjs="+oamagentjs_ver, "alumag="+alumag_ver, "siteoam="+siteoam_ver, "migrationrule="+migrationrule_ver, "pdlvalidator="+pdlvalidator_ver]) {
                    sh '''
                    #!/bin/bash
                    svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_deliver.sh
                    bash mz_ci_deliver.sh -d ${WORKSPACE}/MZ_D_R3
                    '''
                }
                
                r3_version_file = 'MZ_D_R3/commit_version.txt'
                if (fileExists(r3_version_file)) {
                    r3_commit_version = readFile r3_version_file
                }
            },
            "deliver_r4":{
                checkout([$class: 'SubversionSCM', additionalCredentials: [], excludedCommitMessages: '', excludedRegions: '', excludedRevprop: '',
                excludedUsers: '', filterChangelog: false, ignoreDirPropChanges: false, includedRegions: '',
                locations: [[credentialsId: 'd0401375-4c27-45f4-bd34-d1aec06cd524', depthOption: 'infinity', ignoreExternalsOption: true, local: 'MZ_D_R4',
                remote: 'https://svne1.inside.nsn.com/isource/svnroot/BTS_D_MZ_CBTS/branches/CBTS18_FSM4_MZ_0700/']], workspaceUpdater: [$class: 'UpdateWithRevertUpdater']])
                
                withEnv(["RN_VER="+RN_VER, "PS_REL="+PS_REL, "RCP="+RCP, "LTE_MODULE=fsm4", "env="+env_ver, "nodeoam="+nodeoam_ver,
                "nodejs="+nodejs_ver, "racoam="+racoam_ver, "oamagentjs="+oamagentjs_ver, "alumag="+alumag_ver, "siteoam="+siteoam_ver, "migrationrule="+migrationrule_ver, "pdlvalidator="+pdlvalidator_ver]) {
                    sh '''
                    #!/bin/bash
                    svn export --force https://beisop60.china.nsn-net.net/isource/svnroot/BTS_SCM_CLOUD_CB/cbts_ci_script/mz_ci_deliver.sh
                    bash mz_ci_deliver.sh -d ${WORKSPACE}/MZ_D_R4
                    '''
                }
                
                r4_version_file = 'MZ_D_R4/commit_version.txt'
                if (fileExists(r4_version_file)) {
                    r4_commit_version = readFile r4_version_file
                }
            }
        )

        if(r4_commit_version||r3_commit_version){
            currentBuild.description = mz_version+" # RN:r"+RN_VER.split('@')[-1]+" --> D_R3:r"+r3_commit_version+"/D_R4:"+r4_commit_version
        } else {
            currentBuild.description = mz_version+" already commited, no commit this time"
        }
    }
    }
    step([$class: 'Mailer', recipients: 'cbts-cb.scm@nokia.com'])
}
