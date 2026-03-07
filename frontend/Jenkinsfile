import org.jenkinsci.plugins.pipeline.modeldefinition.Utils

library('JenkinsPipelineUtils') _

podTemplate(inheritFrom: 'jenkins-agent kaniko') {
    node(POD_LABEL) {
        stage('Clone repo') {
            git branch: 'main',
                credentialsId: '5f6fbd66-b41c-405f-b107-85ba6fd97f10',
                url: 'https://github.com/pvginkel/DHCPAppUI.git'
        }

        stage('Build dhcp-app') {
            def gitRev = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()

            writeFile file: 'git-rev', text: gitRev

            container('kaniko') {
                helmCharts.kaniko([
                    "registry:5000/dhcpapp-ui:${currentBuild.number}"
                ])
            }

            writeJSON file: 'frontend-build.json', json: [tag: ":${currentBuild.number}", gitRev: gitRev]
            archiveArtifacts artifacts: 'frontend-build.json', fingerprint: true
        }

        stage('Start validation') {
            build job: 'DHCPAppValidation',
                wait: false,
                parameters: [
                    string(name: 'FRONTEND_BUILD', value: "${currentBuild.number}"),
                    string(name: 'TRIGGERED_BY', value: 'frontend')
                ]
        }
    }
}
