import { Stage, StageProps } from 'aws-cdk-lib';
import { Construct } from "constructs";
import { AsynStack } from './async-stack';
import { APP_NAME } from './constants';

export enum PipelineStages {
    BETA = 'Beta',
    PROD = 'Prod'
  }
  
export interface PipelineStageProps extends StageProps {
    stage: PipelineStages;
}

export class PipelineStage extends Stage {
    
    constructor(scope: Construct, id: string, props: PipelineStageProps) {
      super(scope, id, props);
  
      const asynStack = new AsynStack(this, `${APP_NAME}${props.stage}AsyncStack`, {
        stage: props.stage
      });
    }
}