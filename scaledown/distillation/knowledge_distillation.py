'''
Performs vanilla Knowledge Distillation
'''

class KnowledgeDistillation():
    def __init__(self, teacher, student, optimizer, distillation_loss,
            student_loss, temperature=1, metric=None,
            activation=None):
        self.teacher=teacher
        self.student=student
        self._verify_models()

        self.framework=self.teacher._type
        self.optimizer=optimizer
        self.metric=metric
        self.distillation_loss=distillation_loss
        self.student_loss=student_loss
        self.temperature=temperature

    def _verify_models(self):
        if not self.teacher._type==self.student._type:
            raise ValueError("Teacher model and student model should use the same model type")

    def _pytorch_distiller(self, x, y):
        try:
            import torch
            import numpy as np
            import torch.nn.functional as F
        except ImportError as e:
            raise ImportError(f"Cannot import packages {e}")

        if not self.activation:
            self.activation=F.log_softmax

        self.teacher=self.teacher.eval()
        teacher_preds=self.teacher(x)

        self.optimizer.zero_grad()
        student_preds = self.student(x)
        output=self.activation(output, dim=1)
        student_loss = self.distillation_loss(input=output, target=y,
                log_target=True, reduction='batchmean')
        distillation_loss=self.distillation_loss(input=output, target=teacher_preds)
        loss.backward()
        self.optimizer.step()

        results_dict={'student_loss': student_loss, 'distillation_loss': distillation_loss}
        
        return results_dict

    def _tensorflow_distiller(self, x, y):
        '''
        Trains student model for a single iteration on x and y
        '''
        try:
            import tensorflow as tf
            from tensorflow import keras
            from tensorflow.keras import layers
            import numpy as np
        except ImportError as e:
            raise ImportError(f"Cannot import packages {e}")

        if not self.activation:
            self.activation=tf.nn.softmax
        teacher_preds=self.teacher(x, training=False)

        with tf.GradientTape as tape:
            student_preds=self.student(x, training=True)
            student_loss=self.student_loss(y, student_preds)
            distillation_loss=self.distillation_loss(
                    self.activation(teacher_preds/self.temperature, axis=1),
                    self.activation(student_preds/self.temperature, axis=1)
                    )
        trainable_vars=self.student.trainable_vars
        gradients=tape.gradient(distillation_loss, trainable_vars)

        self.optimizer.apply_gradients(zip(gradients, trainable_vars))

        results_dict={'student_loss': student_loss, 'distillation_loss': distillation_loss}
        
        return results_dict

    def train_step(self, data):
        x, y = data
        if self.framework=='tensorflow':
            loss=self._tensorflow_distiller(x, y)
        elif self.framework=='pytorch':
            loss=self._pytorch_distiller(x, y)

        return loss

    def test(self, data):
        '''
        TODO: API to test student model
        '''
        pass
