import org.jenkinsci.plugins.pipeline.modeldefinition.Utils

library('JenkinsPipelineUtils') _

podTemplate(inheritFrom: 'jenkins-agent kaniko') {
    node(POD_LABEL) {
        stage('Clone repo') {
            checkout scm
        }

        stage('Build dhcp-app') {
            def gitRev = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()

            container('kaniko') {
                helmCharts.kaniko([
                    "registry:5000/dhcpapp:${currentBuild.number}"
                ])
            }

            writeJSON file: 'backend-build.json', json: [tag: ":${currentBuild.number}", gitRev: gitRev]
            archiveArtifacts artifacts: 'backend-build.json', fingerprint: true
        }

        stage('Start validation') {
            build job: 'Validation',
                wait: false,
                parameters: [
                    string(name: 'BACKEND_BUILD', value: "${currentBuild.number}"),
                    string(name: 'TRIGGERED_BY', value: 'backend')
                ]
        }
    }
}
