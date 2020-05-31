import React, { Component } from "react";
import EntryList from "./EntryList";
import axios from "axios";
class DiaryHome extends Component {
  state = {entries: []};
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/"+this.props.match.params.id)
      .then((res) => {
        const diary = res.data; //.diaries;
        this.setState({ diary });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }

  render() {
    const diary = this.state;
    return (
      <div className="centered">
        <h1>{diary.title}</h1>

      </div>
    );
  }
}
export default DiaryHome;
