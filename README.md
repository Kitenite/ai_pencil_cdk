# Ai Pencil CDK
The official cdk for Ai Pencil

# Deployment Stages
Our PROD resources will be in `us-west-2` and our BETA resources will be in `us-east-1`.

To publish to just Beta, run:
```
cdk deploy AiPencilBetaAsyncStack
```

To publish to just Prod, run:
```
cdk deploy AiPencilProdAsyncStack
```

To publish to both regions, run:
```
cdk deploy --all
```

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
