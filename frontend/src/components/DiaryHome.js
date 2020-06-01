import React, { Component } from "react";
import EntryList from "./EntryList";
import axios from "axios";
class DiaryHome extends Component {
  state = {title: '', entries: []};
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/"+this.props.match.params.id)
      .then((res) => {
        const diary = res.data; //.diaries;
        this.setState({ title: diary.title, entries: diary.entries});
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }

  render() {
    const title = this.state.title;
    const entries = this.state.entries;
    return (
      <div className="centered">
        <h1>{title}</h1>
            <EntryList entryData={entries}/>
      </div>
    );
  }
}
export default DiaryHome;
