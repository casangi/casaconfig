<?xml version="1.0" encoding="UTF-8"?>
<!--
   This stylesheet converts some of the XML documents belonging to an ASDM dataset version 2
   in order that the resulting files along with the documents which are not transformed
   form an ASDM dataset version 3.

   The transformed elements are those whose root elements are :
   
   ASDM
   CalAmpliTable
   CalAtmosphereTable
   CalDelayTable
   CalFocusTable
   ExecBlockTable
   FocusTable
   MainTable
   PolarizationTable
   SBSummaryTable
   ScanTable
   SubscanTable
   WeatherTable

   Author : Rodrigo Avarias & Michel Caillat
   $Id: sdm-v2v3-alma.xsl,v 1.1 2011/08/10 08:17:23 mcaillat Exp $
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  version="1.0"
    xmlns:cntnr="http://Alma/XASDM/ASDM"
    xmlns:clmpl="http://Alma/XASDM/CalAmpliTable"
    xmlns:clatm="http://Alma/XASDM/CalAtmosphereTable"
    xmlns:cldly="http://Alma/XASDM/CalDelayTable"
    xmlns:clfcs="http://Alma/XASDM/CalFocusTable"
    xmlns:excblk="http://Alma/XASDM/ExecBlockTable"
    xmlns:focus="http://Alma/XASDM/FocusTable"
    xmlns:main="http://Alma/XASDM/MainTable"
    xmlns:plrztn="http://Alma/XASDM/PolarizationTable"
    xmlns:sbsmmr="http://Alma/XASDM/SBSummaryTable"
    xmlns:scn="http://Alma/XASDM/ScanTable"
    xmlns:sbscn="http://Alma/XASDM/SubscanTable"
    xmlns:weathr="http://Alma/XASDM/WeatherTable">
    
    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
    
    <xsl:variable name="d-quote">"</xsl:variable>
    
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>
    
    <!-- Taken from XSLT Cookbook book, only valid for version 1.0 of XSLT standard-->
    <xsl:template name="dup">
        <xsl:param name="input"/>
        <xsl:param name="count" select="2"/>
        <xsl:choose>
            <xsl:when test="not($count) or not($input)"/>
            <xsl:when test="$count = 1">
                <xsl:value-of select="$input"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- If $count is odd append an extra copy of input -->
                <xsl:if test="$count mod 2">
                    <xsl:value-of select="$input"/>
                </xsl:if>
                <!-- Recursively apply template after doubling input and 
                    halving count -->
                <xsl:call-template name="dup">
                    <xsl:with-param name="input" 
                        select="concat($input,$input)"/>
                    <xsl:with-param name="count" 
                        select="floor($count div 2)"/>
                </xsl:call-template>     
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="/ASDM/@schemaVersion|/CalAmpliTable/@schemaVersion|/CalAtmosphereTable/@schemaVersion
        |/CalDelayTable/@schemaVersion|/CalFocusTable/@schemaVersion|/ExecBlockTable/@schemaVersion|/FocusTable/@schemaVersion
        |/MainTable/@schemaVersion|/PolarizationTable/@schemaVersion|/SBSummaryTable/@schemaVersion|/ScanTable/@schemaVersion
        |/SubscanTable/@schemaVersion|/WeatherTable/@schemaVersion | 
        /cntnr:ASDM/@cntnr:schemaVersion|/clmpl:CalAmpliTable/@clmpl:schemaVersion|/clatm:CalAtmosphereTable/@clatm:schemaVersion
        |/cldly:CalDelayTable/@cldly:schemaVersion|/clfcs:CalFocusTable/@clfcs:schemaVersion|/excblk:ExecBlockTable/@excblk:schemaVersion
        |/focus:FocusTable/@focus:schemaVersion|/main:MainTable/@main:schemaVersion|/plrztn:PolarizationTable/@plrztn:schemaVersion
        |/sbsmmr:SBSummaryTable/@sbsmmr:schemaVersion|/scn:ScanTable/@scn:schemaVersion
        |/sbscn:SubscanTable/@sbscn:schemaVersion|/weathr:WeatherTable/@weathr:schemaVersion">
        <xsl:attribute name="schemaVersion">
            <xsl:value-of select="3"/>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" match="/ASDM/@xsi:schemaLocation|/CalAmpliTable/@xsi:schemaLocation
        |/CalAtmosphereTable/@xsi:schemaLocation|/CalDelayTable/@xsi:schemaLocation|/CalFocusTable/@xsi:schemaLocation|
        /ExecBlockTable/@xsi:schemaLocation|/FocusTable/@xsi:schemaLocation|/MainTable/@xsi:schemaLocation
        |/PolarizationTable/@xsi:schemaLocation|/SBSummaryTable/@xsi:schemaLocation|/ScanTable/@xsi:schemaLocation
        |/SubscanTable/@xsi:schemaLocation|WeatherTable/@xsi:schemaLocation
        |/cntnr:ASDM/@xsi:schemaLocation|/clmpl:CalAmpliTable/@xsi:schemaLocation|/clatm:CalAtmosphereTable/@xsi:schemaLocation
        |/cldly:CalDelayTable/@xsi:schemaLocation|/clfcs:CalFocusTable/@xsi:schemaLocation
        |/excblk:ExecBlockTable/@xsi:schemaLocation|/focus:FocusTable/@xsi:schemaLocation|/main:MainTable/@xsi:schemaLocation
        |/plrztn:PolarizationTable/@xsi:schemaLocation|/sbsmmr:SBSummaryTable/@xsi:schemaLocation
        |/scn:ScanTable/@xsi:schemaLocation|/sbscn:SubscanTable/@xsi:schemaLocation|/weathr:WeatherTable/@xsi:schemaLocation">
        <xsl:attribute name="xsi:schemaLocation">
            <xsl:value-of select="translate(.,'2','3')"/>
        </xsl:attribute>
    </xsl:template>
    
    <!--          -->
    <xsl:template match="/ASDM/TimeOfCreation">
        <xsl:copy-of select="."/>
        <xsl:element name="startTimeDurationInXML"></xsl:element>
        <xsl:element name="startTimeDurationInBin"></xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/ASDM" match="/cntnr:ASDM/cntnr:TimeOfCreation">
        <xsl:copy-of select="."/>
        <xsl:element name="startTimeDurationInXML"></xsl:element>
        <xsl:element name="startTimeDurationInBin"></xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalAmpliTable/row/receiverBand" >
        <xsl:copy-of select="."/>
        <xsl:element name="basebandName">
            <xsl:value-of select="'BB_ALL'"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/CalAmpliTable" match="/clmpl:CalAmpliTable/clmpl:row/clmpl:receiverBand" >
        <xsl:copy-of select="."/>
        <xsl:element name="basebandName">
            <xsl:value-of select="'BB_ALL'"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalAtmosphereTable/row/antennaName">
        <xsl:copy-of select="."/>
        <xsl:element name="basebandName">
            <xsl:value-of select="'BB_ALL'"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/CalAtmosphereTable" match="/clatm:CalAtmosphereTable/clatm:row/clatm:antennaName">
        <xsl:copy-of select="."/>
        <xsl:element name="basebandName">
            <xsl:value-of select="'BB_ALL'"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalDelayTable/row/reducedChiSquared">
        <xsl:copy-of select="."/>
        <xsl:element name="appliedDelay"> <xsl:value-of select="concat('1 ', current()/parent::node()/numReceptor)"/>
            <xsl:call-template name="dup">
                <xsl:with-param name="count"><xsl:value-of select="current()/parent::node()/numReceptor"/></xsl:with-param>
            <xsl:with-param name="input"> 0.0</xsl:with-param>
            </xsl:call-template></xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/CalDelayTable" match="/cldly:CalDelayTable/cldly:row/cldly:reducedChiSquared">
        <xsl:copy-of select="."/>
        <xsl:element name="appliedDelay">
            <xsl:value-of select="concat('1 ', current()/parent::node()/cldly:numReceptor)"/>
            <xsl:call-template name="dup">
                <xsl:with-param name="count"><xsl:value-of select="current()/parent::node()/cldly:numReceptor"/></xsl:with-param>
                <xsl:with-param name="input"> 0.0</xsl:with-param>
            </xsl:call-template></xsl:element>
    </xsl:template>
    
    <xsl:template match="/CalFocusTable/row/reducedChiSquared">
        <xsl:copy-of select="."/>
        <xsl:element name="position"> <xsl:value-of select="concat('2 ', current()/parent::node()/numReceptor, ' 3')"/> 
            <xsl:call-template name="dup">
            <xsl:with-param name="count"><xsl:value-of select="current()/parent::node()/numReceptor * 3"/></xsl:with-param>
            <xsl:with-param name="input"> 0.0</xsl:with-param>
            </xsl:call-template></xsl:element>>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/CalFocusTable" match="/clfcs:CalFocusTable/clfcs:row/clfcs:reducedChiSquared">
        <xsl:copy-of select="."/>
        <xsl:element name="position"> <xsl:value-of select="concat('2 ', current()/parent::node()/clfcs:numReceptor, ' 3')"/> 
            <xsl:call-template name="dup">
                <xsl:with-param name="count"><xsl:value-of select="current()/parent::node()/clfcs:numReceptor * 3"/></xsl:with-param>
                <xsl:with-param name="input"> 0.0</xsl:with-param>
            </xsl:call-template></xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/projectId">
        <xsl:element name="projectUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/ExecBlockTable" match="/excblk:ExecBlockTable/excblk:row/excblk:projectId">
        <xsl:element name="projectUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/observerName">
        <xsl:copy-of select="."/>
        <xsl:element name="numObservingLog">1</xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/ExecBlockTable" match="/excblk:ExecBlockTable/excblk:row/excblk:observerName">
        <xsl:copy-of select="."/>
        <xsl:element name="numObservingLog">1</xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/observingLog">
        <xsl:element name="observingLog"><xsl:value-of select="concat('1 1 ', $d-quote, normalize-space(.), $d-quote)"/></xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/ExecBlockTable" match="/excblk:ExecBlockTable/excblk:row/excblk:observingLog">
        <xsl:element name="observingLog"><xsl:value-of select="concat('1 1 ', $d-quote, normalize-space(.), $d-quote)"/></xsl:element>
    </xsl:template>
    
    <xsl:template match="/ExecBlockTable/row/sessionReference">
        <xsl:choose>
            <xsl:when test="count(./EntityRef) = 0">
                <xsl:element name="sessionReference">
                    <xsl:element name="EntityRef"> 
                        <xsl:attribute name="entityId"><xsl:value-of select="'uid://A000/X000000/X0'"/></xsl:attribute>
                        <xsl:attribute name="partId"><xsl:value-of select="'X00000000'"/></xsl:attribute>
                        <xsl:attribute name="entityTypeName"><xsl:value-of select="'OUSStatus'"/></xsl:attribute>
                        <xsl:attribute name="documentVersion"><xsl:value-of select="'1.0'"/></xsl:attribute>
                    </xsl:element>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/ExecBlockTable" match="/excblk:ExecBlockTable/excblk:row/excblk:sessionReference">
        <xsl:choose>
            <xsl:when test="count(./excblk:EntityRef) = 0">
                <xsl:element name="sessionReference">
                    <xsl:element name="EntityRef"> 
                        <xsl:attribute name="entityId"><xsl:value-of select="'uid://A000/X000000/X0'"/></xsl:attribute>
                        <xsl:attribute name="partId"><xsl:value-of select="'X00000000'"/></xsl:attribute>
                        <xsl:attribute name="entityTypeName"><xsl:value-of select="'OUSStatus'"/></xsl:attribute>
                        <xsl:attribute name="documentVersion"><xsl:value-of select="'1.0'"/></xsl:attribute>
                    </xsl:element>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template> 
    
    <xsl:template match="/ExecBlockTable/row/sbSummary"/>
    <xsl:template xmlns="http://Alma/XASDM/ExecBlockTable" match="/excblk:ExecBlockTable/excblk:row/excblk:sbSummary"/>
    <xsl:template match="/ExecBlockTable/row/flagRow"/>
    <xsl:template xmlns="http://Alma/XASDM/ExecBlockTable" match="/excblk:ExecBlockTable/excblk:row/excblk:flagRow"/>
    
    <xsl:template match="/FocusTable/row/focusOffset" >
        <xsl:copy-of select="."/>
        <xsl:element name="focusRotationOffset"><xsl:value-of select="'1 2 0.0 0.0'"/></xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/FocusTable" match="/focus:FocusTable/focus:row/focus:focusOffset">
        <xsl:copy-of select="."/>
        <xsl:element name="focusRotationOffset"><xsl:value-of select="'1 2 0.0 0.0'"/></xsl:element>
    </xsl:template>
    
    <xsl:template match="/MainTable/row/dataOid">
        <xsl:element name="dataUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/MainTable" match="/main:MainTable/main:row/main:dataOid">
        <xsl:element name="dataUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    
    <xsl:template match="/PolarizationTable/row/flagRow" />
    <xsl:template xmlns="http://Alma/XASDM/PolarizationTable" match="/plrztn:PolarizationTable/plrztn:row/plrztn:flagRow" />
    
    <xsl:template match="/SBSummaryTable/row/obsUnitSetId">
        <xsl:element name="obsUnitSetUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/SBSummaryTable" match="/sbsmmr:SBSummaryTable/sbsmmr:row/sbsmmr:obsUnitSetId">
        <xsl:element name="obsUnitSetUID">
            <xsl:apply-templates select="@* | node()"></xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/ScanTable/row/numSubScan">
        <xsl:element name="numSubscan">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/ScanTable" match="/scn:ScanTable/scn:row/scn:numSubScan">
        <xsl:element name="numSubscan">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/ScanTable/row/flagRow"/>
    <xsl:template xmlns="http://Alma/XASDM/ScanTable" match="/scn:ScanTable/scn:row/scn:flagRow"/>

    <xsl:template match="/SubscanTable/row/numberIntegration">
        <xsl:element name="numIntegration">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/SubscanTable" match="/sbscn:SubscanTable/sbscn:row/sbscn:numberIntegration">
        <xsl:element name="numIntegration">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/SubscanTable/row/numberSubintegration">
        <xsl:element name="numSubintegration">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template xmlns="http://Alma/XASDM/SubscanTable" match="/sbscn:SubscanTable/sbscn:row/sbscn:numberSubintegration">
        <xsl:element name="numSubintegration">
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="/SubscanTable/row/flagRow"/>
    <xsl:template xmlns="http://Alma/XASDM/SubscanTable" match="/sbscn:SubscanTable/sbscn:row/sbscn:flagRow"/>
    
    
    <xsl:template match="/WeatherTable/row/pressureFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:pressureFlag"/>
    
    <xsl:template match="/WeatherTable/row/relHumidityFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:relHumidityFlag"/>
    
    <xsl:template match="/WeatherTable/row/temperatureFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:temperatureFlag"/>
    
    <xsl:template match="/WeatherTable/row/windDirectionFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:windDirectionFlag"/>
    
    <xsl:template match="/WeatherTable/row/windSpeedFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:windSpeedFlag"/>
    
    <xsl:template match="/WeatherTable/row/windMaxFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:windMaxFlag"/>
    
    <xsl:template match="/WeatherTable/row/dewPointFlag"/>
    <xsl:template xmlns="http://Alma/XASDM/WeatherTable" match="/weathr:WeatherTable/weathr:row/weathr:dewPointFlag"/>
    
</xsl:stylesheet>


