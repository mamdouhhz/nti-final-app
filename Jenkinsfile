pipeline {
    agent any

    environment {
        ECR_REPO          = "463470958932.dkr.ecr.us-east-2.amazonaws.com/nti-final-ecr"
        AWS_REGION        = "us-east-2"
        EKS_CLUSTER       = "nti-final-eks"
        SONAR_PROJECT_KEY = "mamdouhhz_nti-final-app"
        SONAR_ORG         = "mamdouhhz"
        BUILD_TAG         = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    script {
                        def scannerHome = tool 'SonarScanner'
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.organization=${SONAR_ORG} \
                              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                              -Dsonar.sources=. \
                              -Dsonar.host.url=https://sonarcloud.io
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                sh """
                    docker build -t ${ECR_REPO}:backend-${BUILD_TAG} ./app/backend
                    docker build -t ${ECR_REPO}:frontend-${BUILD_TAG} ./app/frontend
                """
            }
        }

        stage('Trivy Scan') {
            steps {
                sh """
                    trivy image --severity HIGH,CRITICAL --exit-code 1 ${ECR_REPO}:backend-${BUILD_TAG}
                    trivy image --severity HIGH,CRITICAL --exit-code 1 ${ECR_REPO}:frontend-${BUILD_TAG}
                """
            }
        }

        stage('Push to ECR') {
            steps {
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}
                    docker push ${ECR_REPO}:backend-${BUILD_TAG}
                    docker push ${ECR_REPO}:frontend-${BUILD_TAG}
                """
            }
        }

        stage('Deploy to EKS') {
            when {
                branch 'prod'
            }
            steps {
                sh """
                    aws eks update-kubeconfig --name ${EKS_CLUSTER} --region ${AWS_REGION}
                    helm upgrade --install nti-final-project ./k8s/helm/app-chart \
                        --namespace nti-final-project \
                        --set backend.image.repository=${ECR_REPO} \
                        --set backend.image.tag=backend-${BUILD_TAG} \
                        --set frontend.image.repository=${ECR_REPO} \
                        --set frontend.image.tag=frontend-${BUILD_TAG}
                """
            }
        }
    }

    post {
        always {
            sh "docker system prune -f || true"
        }
        failure {
            echo "Pipeline failed on branch ${env.BRANCH_NAME} — check the stage logs above."
        }
    }
}