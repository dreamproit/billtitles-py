@Library('jenkins-shared-lib') _

eksPipeline{
    project = "billtitles-py"
    awsProjectMap = ["739065237548": "develop,stage,prod,preprod,helm_chart"]
    awsClusterMap = ["739065237548": "eks-cluster-main"]
    deployMap = ["helm_chart": "dev", "stage": "stage", "prod": "prod"]
    artifactName = "billtitles-py"
    promotionMap = ["prod": ["from": "stage"], "preprod": ["from": "stage"]]
    listCredentials = [
        "POSTGRES_HOST",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
        "SECRET_KEY"
    ]
}
