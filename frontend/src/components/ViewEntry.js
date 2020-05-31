import React, { Component } from "react";
import "./styles.css";
class ViewEntry extends Component {
initialState = {
  textBody: this.props.location.state,
}
state = this.initialState;
handleChange = event => {
 const { textBody, value } = event.target

 this.setState({
   [textBody]: value,
 })
}
render() {
 const { textBody} = this.state;

 return (
   <form>
     <label htmlFor="textBody">TextBody</label>
     <input
       type="text"
       name="text"
       id="text"
       value={textBody}
       onChange={this.handleChange} />
    </form>
  );
  }
}
export default ViewEntry;
