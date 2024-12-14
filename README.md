This is TinySinkDetect 🍽️🚀! A system to train your tinyengine model to classify dirty sinks from clean sinks. See more information about TinySinkDetect here. 

Using the system is simple! Follow these steps:

1. Refer to [tinyengine demo](https://github.com/mit-han-lab/tinyengine/tree/main/tutorial/training) for instructions on model setup.

2. Switch the run target in STM32CubeIDE to sink_detect/binaries/sink_detect_mcunet.elf by going to Run -> Run Configurations (Expand Screen)-> STM32 C/C++ Application -> TTE_demo_mcunet Debug -> Browse -> Navigate to sink_detect/binaries/sink_detect_mcunet.elf and select -> Run

3. Run trainer.py with arguments as follows

`trainer.py {csv_file_name} {training_schedule}`

train_{csv_file_name}.csv and val_{csv_file_name}.csv will be files with img_file, cls (1 is clean, 2 is dirty), correct (True or False)

training schedule must be >1, with 2 performing an alternating training scheme, 3 performing a 2:1 training scheme (dirty to clean), and so forth. 

Sink Data Folder Structure:
```
sink_data/
├── train/
│   ├── clean_sink
│   │  ├── img1.JPG
│   ├── dirty_sink
│   │  ├── img1.JPG
├── train/
│   ├── clean_sink
│   │  ├── img1.JPG
│   ├── dirty_sink
│   │  ├── img1.JPG
├── val/
│   ├── clean_sink
│   │  ├── img1.JPG
│   ├── dirty_sink
│   │  ├── img1.JPG
```
