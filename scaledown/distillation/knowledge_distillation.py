
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
        except Exception as e:
            raise ImportError("Cannot import torch and numpy packages: {e}")

        if not self.activation:
            self.activation=F.log_softmax

        self.teacher=self.teacher.eval()
        train_loss=0
        prev=teacher_model.fc2.weight
        teacher_preds=self.teacher(x)

        self.optimizer.zero_grad()
        student_preds = self.student(x)
        output=self.activation(output, dim=1)
        loss = self.distillation_loss(input=output, target=target,
                log_target=True, reduction='batchmean')
        train_loss+=loss
        loss.backward()
        self.optimizer.step()

    def _tensorflow_distiller(self, x, y):
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

    def train_step(self, data):
        x, y = data
        if self.framework=='tensorflow':
            self._tensorflow_distiller(x, y)
        elif self.framework=='pytorch':
            self._pytorch_distiller(x, y)

    def test(self, data):
        pass
