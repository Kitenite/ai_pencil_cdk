import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CodePipeline, CodePipelineSource, ShellStep } from 'aws-cdk-lib/pipelines';
import { APP_NAME } from './constants';
import { PipelineStage, PipelineStages } from './stage';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new CodePipeline(this, `${APP_NAME}Pipeline`, {
      pipelineName: `${APP_NAME}Pipeline`,
      synth: new ShellStep('Synth', {
        input: CodePipelineSource.gitHub('Kitenite/ai_pencil_cdk', 'main'),
        commands: ['npm ci', 'npm run build', 'npx cdk synth']
      })
    });

    pipeline.addStage(new PipelineStage(this, `${APP_NAME}BetaStage`, {
      stage: PipelineStages.BETA
    }));

    pipeline.addStage(new PipelineStage(this, `${APP_NAME}ProdStage`, {
      stage: PipelineStages.BETA
    }));
  }
}