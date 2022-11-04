using Microsoft.Win32;
using System.Collections.ObjectModel;
using System.Collections.Generic;
using Newtonsoft.Json;
using System.ComponentModel;
using System.IO;

namespace Wsycarlos.AutoDerby
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
                Label = "\u81ea\u52a8\u517b\u9a6c",
                Value = "nurturing",
            });
            Add(new Option()
            {
                Label = "\u81ea\u52a8\u9009\u62e9\u9009\u9879",
                Value = "auto_options",
            });
            Add(new Option()
            {
                Label = "\u9009\u9879\u6548\u679c\u63d0\u793a",
                Value = "option_tips",
            });
        }
    }

    public class AutoNuturingOption
    {
        public List<int> value;
        public Dictionary<string, int> races;
    }

    public enum RACE_GRADE
    {
        GRADE_DEBUT = 900,
        GRADE_NOT_WINNING = 800,
        GRADE_PRE_OP = 700,
        GRADE_OP = 400,
        GRADE_G3 = 300,
        GRADE_G2 = 200,
        GRADE_G1 = 100
    }

    public class Race_Data
    {
        public string name;
        public RACE_GRADE grade;
    }

    public class PresetData
    {
        public Dictionary<string, AutoNuturingOption> data = null;

        public Dictionary<string, Race_Data> races = null;

        public Dictionary<string, string> loc = null;

        private string preset_path = null;

        public PresetData(string preset_path, string race_path, string loc_path)
        {
            this.preset_path = preset_path;
            string preset_json_text = File.ReadAllText(preset_path);
            data = JsonConvert.DeserializeObject<Dictionary<string, AutoNuturingOption>>(preset_json_text);
            loc = new Dictionary<string, string>();
            string[] loc_texts = File.ReadAllLines(loc_path);
            foreach(var loc_text in loc_texts)
            {
                var elements = loc_text.Split(',');
                loc[elements[0]]=elements[1];
            }
            string[] race_json_texts = File.ReadAllLines(race_path);
            races = new Dictionary<string, Race_Data>();
            foreach(var race_text in race_json_texts)
            {
                var race_data = JsonConvert.DeserializeObject<Race_Data>(race_text);
                if(race_data.name.Contains("\u0055\u0052\u0041\u30d5\u30a1\u30a4\u30ca\u30eb\u30ba")||race_data.name.Contains("\u30c8\u30a5\u30a4\u30f3\u30af\u30eb\u30b9\u30bf\u30fc\u30af\u30e9\u30a4\u30de\u30c3\u30af\u30b9"))
                {
                }
                else if(loc.ContainsKey(race_data.name))
                {
                    races[loc[race_data.name]] = race_data;
                }
                else
                {
                }
            }
        }

        public void Save()
        {
            var json_text = JsonConvert.SerializeObject(data, Newtonsoft.Json.Formatting.Indented);
            File.WriteAllText(preset_path, json_text);
        }
    }

    public class PresetOptions : ObservableCollection<Option>
    {
        public PresetOptions(PresetData preset_data)
        {
            foreach(var k in preset_data.data.Keys)
            {
                Add(new Option()
                {
                    Label = k,
                    Value = k,
                }
                );
            }
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

        private const string RegistryPath = @"Software\wsycarlos\auto-derby";

        private RegistryKey key;

        public PresetData preset_data;

        public DataContext(PresetData data)
        {
            this.preset_data = data;
            this.key = Registry.CurrentUser.OpenSubKey(RegistryPath, true);
            if (this.key == null)
            {
                this.key = Registry.CurrentUser.CreateSubKey(RegistryPath);
            }

            this.JobOptions1 = new JobOptions();
            this.PresetOptions1 = new PresetOptions(preset_data);
            this.G1RaceOptions = new RaceOptions(preset_data, new RACE_GRADE[1]{RACE_GRADE.GRADE_G1});
            this.G2RaceOptions = new RaceOptions(preset_data, new RACE_GRADE[1]{RACE_GRADE.GRADE_G2});
            this.G3RaceOptions = new RaceOptions(preset_data, new RACE_GRADE[1]{RACE_GRADE.GRADE_G3});
            this.OtherRaceOptions = new RaceOptions(preset_data, new RACE_GRADE[2]{RACE_GRADE.GRADE_OP, RACE_GRADE.GRADE_PRE_OP});
        }
        ~DataContext()
        {
            preset_data.Save();
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
                return (int)key.GetValue("PauseIfRaceOrderGt", 7);
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
                return (string)key.GetValue("Plugins", "prompt_on_end,pause_before_race_continue,auto_crane,\u0053\u0053\u0052\u99ff\u5ddd\u624b\u7db1,wsy_custom_training");
            }
            set
            {
                key.SetValue("Plugins", value);
                OnPropertyChanged("Plugins");
            }
        }

        public string ADBAddress
        {
            get
            {
                return (string)key.GetValue("ADBAddress", "127.0.0.1:7555");
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
                return (int)key.GetValue("Debug", 0) != 0;
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

        public string Preset
        {
            get
            {
                return (string)key.GetValue("Preset", "");
            }
            set
            {
                key.SetValue("Preset", value);
                OnPropertyChanged("TargetSpeed");
                OnPropertyChanged("TargetStamina");
                OnPropertyChanged("TargetPower");
                OnPropertyChanged("TargetGut");
                OnPropertyChanged("TargetWisdom");
            }
        }

        public PresetOptions PresetOptions1
        { get; set; }

        public int TargetSpeed
        {
            get
            {
                return preset_data.data[Preset].value[0];
            }
            set
            {
                preset_data.data[Preset].value[0] = value;
                OnPropertyChanged("TargetSpeed");
            }
        }

        public int TargetStamina
        {
            get
            {
                return preset_data.data[Preset].value[1];
            }
            set
            {
                preset_data.data[Preset].value[1] = value;
                OnPropertyChanged("TargetStamina");
            }
        }

        public int TargetPower
        {
            get
            {
                return preset_data.data[Preset].value[2];
            }
            set
            {
                preset_data.data[Preset].value[2] = value;
                OnPropertyChanged("TargetPower");
            }
        }

        public int TargetGut
        {
            get
            {
                return preset_data.data[Preset].value[3];
            }
            set
            {
                preset_data.data[Preset].value[3] = value;
                OnPropertyChanged("TargetGut");
            }
        }

        public int TargetWisdom
        {
            get
            {
                return preset_data.data[Preset].value[4];
            }
            set
            {
                preset_data.data[Preset].value[4] = value;
                OnPropertyChanged("TargetWisdom");
            }
        }

        public class RaceOptions : ObservableCollection<Option>
        {
            public RaceOptions(PresetData preset_data, RACE_GRADE[] grades)
            {
                foreach(var k in preset_data.races.Keys)
                {
                    foreach(var grade in grades)
                    {
                        if(preset_data.races[k].grade == grade)
                        {
                            Add(new Option()
                            {
                                Label = k,
                                Value = k,
                            }
                            );
                        }
                    }
                }
            }
        }

        public RaceOptions G1RaceOptions
        { get; set; }

        private string _G1Race;
        public string G1Race
        {
            get
            {
                return _G1Race;
            }
            set
            {
                _G1Race = value;
                OnPropertyChanged("G1Value");
            }
        }

        public int G1Value
        {
            get
            {
                return preset_data.data[Preset].races[G1Race];
            }
            set
            {
                preset_data.data[Preset].races[G1Race] = value;
            }
        }

        public RaceOptions G2RaceOptions
        { get; set; }

        private string _G2Race;
        public string G2Race
        {
            get
            {
                return _G2Race;
            }
            set
            {
                _G2Race = value;
                OnPropertyChanged("G2Value");
            }
        }

        public int G2Value
        {
            get
            {
                return preset_data.data[Preset].races[G2Race];
            }
            set
            {
                preset_data.data[Preset].races[G2Race] = value;
            }
        }

        public RaceOptions G3RaceOptions
        { get; set; }

        private string _G3Race;
        public string G3Race
        {
            get
            {
                return _G3Race;
            }
            set
            {
                _G3Race = value;
                OnPropertyChanged("G3Value");
            }
        }

        public int G3Value
        {
            get
            {
                return preset_data.data[Preset].races[G3Race];
            }
            set
            {
                preset_data.data[Preset].races[G3Race] = value;
            }
        }

        public RaceOptions OtherRaceOptions
        { get; set; }

        private string _OtherRace;
        public string OtherRace
        {
            get
            {
                return _OtherRace;
            }
            set
            {
                _OtherRace = value;
                OnPropertyChanged("OtherValue");
            }
        }

        public int OtherValue
        {
            get
            {
                return preset_data.data[Preset].races[OtherRace];
            }
            set
            {
                preset_data.data[Preset].races[OtherRace] = value;
            }
        }
    }
}
