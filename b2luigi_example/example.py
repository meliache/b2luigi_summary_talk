import b2luigi
import random


class MyNumberTask(b2luigi.Task):
    other_param = b2luigi.Parameter(default="A")
    random_seed = b2luigi.IntParameter()

    batch_system = "htcondor"

    htcondor_settings = {
        "request_cpus": 1,
        "request_memory": "100 MB",
        "+requestRuntime": 60 * 3,
    }

    def output(self):
        yield self.add_to_output("output_file.txt")

    def run(self):
        print("I am now starting a task")
        random.seed(self.random_seed)
        random_number = random.random()

        with open(self.get_output_file_name("output_file.txt"), "w") as f:
            f.write(f"{random_number}\n")


class MyAverageTask(b2luigi.WrapperTask):
    htcondor_settings = {
        "request_cpus": 1,
        "request_memory": "200 MB",
        "+requestRuntime": 60 * 3,
    }
    n_random = b2luigi.IntParameter()

    def requires(self):
        for i in range(self.n_random):
            yield self.clone(MyNumberTask, random_seed=i)

    def output(self):
        yield self.add_to_output("average.txt")

    def run(self):
        print("I am now starting the average task")

        # Build the mean
        summed_numbers = 0
        counter = 0
        for input_file in self.get_input_file_names("output_file.txt"):
            with open(input_file, "r") as f:
                summed_numbers += float(f.read())
                counter += 1

        average = summed_numbers / counter

        with open(self.get_output_file_name("average.txt"), "w") as f:
            f.write(f"{average}\n")


if __name__ == "__main__":
    b2luigi.set_setting("result_dir", "./example_outputs")
    b2luigi.process(MyAverageTask(n_random=60), workers=50)
