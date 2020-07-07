import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# from server_method import _server_


class Client(object):
    def __init__(self):
        self.df = pd.read_csv("mnist 10k test data.csv")
        self.INPUT_SHAPE = (784,)
        self.OUTPUT_SHAPE = 10
        # Put atleast 1 hidden layer
        self.HIDDEN_LAYERS = [100]
        self.LABEL = "Label"
        self. SPLIT_SIZE = 10
        self.EPOCHS = 1

        self.x = self.df.drop([self.LABEL], 1)
        self.y = self.df[self.LABEL]
        self.encoder = LabelEncoder()
        self.encoder.fit(self.y)
        self.y = self.encoder.transform(self.y)
        self.x, self.x_test, self.y, self.y_test = train_test_split(
            self.x, self.y, test_size=0.3, random_state=0
        )
        self.x_test, self.x_valid, self.y_test, self.y_valid = train_test_split(
            self.x_test, self.y_test, test_size=0.5, random_state=0
        )
        self.X_train, self.Y_train = [], []
        self.split_data(self.x, self.y, self.SPLIT_SIZE)

        self.models = []
        self.metrics = []
        self.m = (self.model_build()).get_weights()
        self.final_model = self.model_build()

    def split_data(self, x, y, SPLIT_SIZE):
        for i in range(0, SPLIT_SIZE):
            self.X_train.append(
                x[int((i * len(x) / SPLIT_SIZE)) : (int((i + 1) * len(x) / SPLIT_SIZE))]
            )
            self.Y_train.append(
                y[(int(i * len(x) / SPLIT_SIZE)) : (int((i + 1) * len(x) / SPLIT_SIZE))]
            )

    def model_build(self):
        model1 = tf.keras.models.Sequential()
        model1.add(
            tf.keras.layers.Dense(
                self.HIDDEN_LAYERS[0], input_shape=self.INPUT_SHAPE, activation="relu"
            )
        )
        for num in range(1, len(self.HIDDEN_LAYERS)):
            model1.add(
                tf.keras.layers.Dense(self.HIDDEN_LAYERS[num], activation="relu")
            )
        model1.add(tf.keras.layers.Dense(self.OUTPUT_SHAPE, activation="softmax"))
        model1.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        return model1

    # make it so that nothing server does is in this and it returen all the updated models
    def Federated_model(self, i, m):
        # sm = _server_()
        self.m = m
        print("Step ", i, " : ")
        if i != 0:
            for j in range(0, self.SPLIT_SIZE):
                self.models[j].set_weights(self.m)
        else:
            for j in range(0, self.SPLIT_SIZE):
                self.models.append(self.model_build())

        # print(self.X_train.shape)
        # print(self.Y_train.shape)
        for j in range(0, self.SPLIT_SIZE):
            self.models[j].fit(
                self.X_train[j], self.Y_train[j], epochs=self.EPOCHS
            )  # this is where client generates weights
            # models[j].evaluate(x_test, y_test)
        # m = sm.weights_update(self.models)  # these are the averaged weights outght to be generated by server
        self.final_model.set_weights(self.m)
        print("Federated model: ")
        self.loss, self.acc = self.final_model.evaluate(self.x_test, self.y_test)
        self.metrics.append(self.acc)
        """
        self.final_model.set_weights(self.m)
        self.final_model.evaluate(self.x_test, self.y_test)
        """
        self.all_weights = []
        for j in range(0, self.SPLIT_SIZE):
            self.all_weights.append(self.models[j].get_weights())
        return self.all_weights

