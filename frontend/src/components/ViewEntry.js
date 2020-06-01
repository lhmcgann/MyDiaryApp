import React, { Component } from "react";
import "../styles.css";
import axios from "axios";
class ViewEntry extends Component {
  componentDidMount(){
    axios
      .get("http://localhost:5000/diaries/140697768905416/entries/"
      +this.propss.match.params.e_id)
      .then((res) => {
        const entry = res.data; //.diaries;
        this.setState({ entry });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
state = {entry: []};
handleChange = event => {
 const { entry, value } = event.target

 this.setState({
   [entry]: value,
 })
}
render() {
 const { entry} = this.state;

 return (
   <form>
     <label htmlFor="textBody">TextBody</label>
     <input
       type="text"
       name="text"
       id="text"
       value={entry}
       onChange={this.handleChange} />
    </form>
  );
  }
}
export default ViewEntry;
