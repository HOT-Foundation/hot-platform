pipeline {
    agent {
        node {
            label 'Infra'
        }
    }
    stages {
        stage ('Clear Worksapce') {
            steps {
                sh 'sudo rm -rf .[!.]* *'
                deleteDir()
            }
        }
        stage ('Clear container') {
            steps {
                sh 'docker rm -f $(docker ps -a -q) || echo "No containers"'
            }
        }
        stage ('Clone Source Code') {
            steps {
                checkout scm
            }
        }  
        stage ('Build Docker Image') {
            steps {
                sh './build.sh'
            }
        }
        stage ('Reset') {
            steps {
                sh './reset.sh'
            }
        }
        stage ('Run Test') {
            steps {
                sh './runtests.sh'
            }
        }
        stage ('Push Docker Image') {
            steps {
                sh 'docker push registry-hotnow.proteus-tech.com/hotnow-htkn-platform:$(git describe --always)'
            }
        }
/*
        stage ('Push Docker Image If Tag Name Is Hotfix') {
            when {environment name: 'GIT_TAG_NAME', value: 'hotfix'}
            steps {
                sh 'docker push registry-hotnow.proteus-tech.com/hotnow-token-service:${GIT_TAG_NAME}'
            }
        }
        stage ('Push Docker Image If Tag Name Is Release') {
            when {environment name: 'GIT_TAG_NAME', value: 'release'}
            steps {
                sh 'docker push registry-hotnow.proteus-tech.com/hotnow-token-service:${GIT_TAG_NAME}'
            }
        }
*/
    }
}
