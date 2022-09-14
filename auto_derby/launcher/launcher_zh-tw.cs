using Microsoft.Win32;
using System.Collections.ObjectModel;
using System.ComponentModel;

namespace NateScarlet.AutoDerby
{
    public class Option
    {
        public string Label
        { get; set; }

        public string Value
        { get; set; }
    }

    public class JobOptions : ObservableCollection<Option>
    {
        public JobOptions()
        {
            Add(new Option()
            {
                Label = "Nurturing",
                Value = "nurturing",
            });
            Add(new Option()
            {
                Label = "Auto_Options",
                Value = "auto_options",
            });
            Add(new Option()
            {
                Label = "Option_Tips",
                Value = "option_tips",
            });
        }
    }

    public class DistanceOptions : ObservableCollection<Option>
    {
        public DistanceOptions()
        {
            Add(new Option()
            {
                Label = "Short",
                Value = "short",
            });
            Add(new Option()
            {
                Label = "Miles",
                Value = "miles",
            });
            Add(new Option()
            {
                Label = "Medium",
                Value = "medium",
            });
            Add(new Option()
            {
                Label = "Long",
                Value = "long",
            });
            Add(new Option()
            {
                Label = "Custom",
                Value = "custom",
            });
        }
    }

    public class DataContext : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;
        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChangedEventHandler handler = PropertyChanged;
            if (handler != null) handler(this, new PropertyChangedEventArgs(propertyName));
        }

        private const string RegistryPath = @"Software\NateScarlet\auto-derby";

        private RegistryKey key;

        public DataContext()
        {
            this.key = Registry.CurrentUser.OpenSubKey(RegistryPath, true);
            if (this.key == null)
            {
                this.key = Registry.CurrentUser.CreateSubKey(RegistryPath);
            }

            this.JobOptions1 = new JobOptions();
            this.DistanceOptions1 = new DistanceOptions();
        }
        ~DataContext()
        {
            key.Dispose();
        }

        public string DefaultSingleModeChoicesDataPath;
        public string SingleModeChoicesDataPath
        {
            get
            {
                return (string)key.GetValue("SingleModeChoicesDataPath", DefaultSingleModeChoicesDataPath);
            }
            set
            {
                key.SetValue("SingleModeChoicesDataPath", value);
                OnPropertyChanged("SingleModeChoicesDataPath");
            }
        }

        public string DefaultPythonExecutablePath;
        public string PythonExecutablePath
        {
            get
            {
                return (string)key.GetValue("PythonExecutablePath", DefaultPythonExecutablePath);
            }
            set
            {
                key.SetValue("PythonExecutablePath", value);
                OnPropertyChanged("PythonExecutablePath");
            }
        }

        public int PauseIfRaceOrderGt
        {
            get
            {
                return (int)key.GetValue("PauseIfRaceOrderGt", 5);
            }
            set
            {
                key.SetValue("PauseIfRaceOrderGt", value, RegistryValueKind.DWord);
                OnPropertyChanged("PauseIfRaceOrderGt");
            }
        }

        public string Plugins
        {
            get
            {
                return (string)key.GetValue("Plugins", "");
            }
            set
            {
                key.SetValue("Plugins", value);
                OnPropertyChanged("Plugins");
            }
        }

        public string Force_Races
        {
            get
            {
                return (string)key.GetValue("Force_Races", "");
            }
            set
            {
                key.SetValue("Force_Races", value);
                OnPropertyChanged("Force_Races");
            }
        }

        public string Prefered_Races
        {
            get
            {
                return (string)key.GetValue("Prefered_Races", "");
            }
            set
            {
                key.SetValue("Prefered_Races", value);
                OnPropertyChanged("Prefered_Races");
            }
        }

        public string Avoid_Races
        {
            get
            {
                return (string)key.GetValue("Avoid_Races", "");
            }
            set
            {
                key.SetValue("Avoid_Races", value);
                OnPropertyChanged("Avoid_Races");
            }
        }
        
        public string TargetTrainingValues
        {
            get
            {
                return (string)key.GetValue("TargetTrainingValues", "600,600,600,400,400");
            }
            set
            {
                key.SetValue("TargetTrainingValues", value);
                OnPropertyChanged("TargetTrainingValues");
            }
        }

        public string ADBAddress
        {
            get
            {
                return (string)key.GetValue("ADBAddress", "");
            }
            set
            {
                key.SetValue("ADBAddress", value);
                OnPropertyChanged("ADBAddress");
            }
        }

        public bool Debug
        {
            get
            {
                return (int)key.GetValue("Debug", 1) != 0;
            }
            set
            {
                key.SetValue("Debug", value, RegistryValueKind.DWord);
                OnPropertyChanged("Debug");
            }
        }

        public bool CheckUpdate
        {
            get
            {
                return (int)key.GetValue("CheckUpdate", 0) != 0;
            }
            set
            {
                key.SetValue("CheckUpdate", value, RegistryValueKind.DWord);
                OnPropertyChanged("CheckUpdate");
            }
        }


        public string Job
        {
            get
            {
                return (string)key.GetValue("Job", "nurturing");
            }
            set
            {
                key.SetValue("Job", value);
                OnPropertyChanged("Job");
            }
        }

        public JobOptions JobOptions1
        { get; set; }


        public string Distance
        {
            get
            {
                return (string)key.GetValue("Distance", "short");
            }
            set
            {
                key.SetValue("Distance", value);
                OnPropertyChanged("Distance");
            }
        }

        public DistanceOptions DistanceOptions1
        { get; set; }
    }
}
